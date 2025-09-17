# backend/services/gemini_predict.py
import os
import json
import google.generativeai as genai
from db.database_utils import get_db_connection

# --------------------------------------------------------------------------
# 1. Gemini API 호출을 위한 시스템 프롬프트
# --------------------------------------------------------------------------
SYSTEM_PROMPT_WEIGHT_PREDICTION = """
You are an expert AI specializing in estimating the weight of individual objects found in luggage. Your primary goal is to provide a unique and plausible weight for EACH item based on the provided data.

Your task is to predict the final weight for a list of items provided in a JSON array. Each object in the input array represents a **separate, unique instance** of a detected item.

**Input Data Schema (for each item):**
- `id`: The unique identifier for the specific item instance.
- `item_name`: The name of the item.
- `avg_weight`: The average or reference weight of this item type (e.g., "350g"). This is your primary baseline.
- `weight_range`: The typical weight range for this item type (e.g., "200-500g").
- `bbox_ratio`: A decimal representing the item's size in the image. A larger ratio means the item appears larger.

**Core Reasoning Logic:**
1.  **Baseline:** Use the `avg_weight` as your starting point.
2.  **Contextual Adjustment:** Your primary task is to intelligently adjust this baseline using the `bbox_ratio` and your real-world knowledge.
    - For items where size often correlates with weight (e.g., a laptop, a bottle of water), a larger `bbox_ratio` should lead to a more significant weight increase within the `weight_range`.
    - For items where size is less indicative of weight (e.g., a folded T-shirt, an item close to the camera), the adjustment from the `avg_weight` should be more subtle.
3.  **Crucial Differentiation:** While applying your real-world knowledge, you should still ensure that two instances of the same `item_name` with different `bbox_ratio`s **generally result in different `predicted_weight_value`s**. Avoid assigning a single, static weight to all instances of an item type. Your goal is to provide nuanced, instance-specific predictions.
4.  **Plausibility Check:** The final `predicted_weight_value` must be a realistic number within the given `weight_range`.

**Output Format Rules:**
- You MUST respond ONLY with a valid JSON array.
- Do not include any other text, explanations, or markdown formatting like ```json.
- Each object in the array must follow this exact structure:
  `{"id": <number>, "predicted_weight_value": <number>, "predicted_weight_unit": "<'g' or 'kg'>"}`

**Example Input (showing multiple instances):**
[
  {"id": 101, "item_name": "T-Shirt", "avg_weight": "150g", "weight_range": "100-200g", "bbox_ratio": 0.15},
  {"id": 102, "item_name": "T-Shirt", "avg_weight": "150g", "weight_range": "100-200g", "bbox_ratio": 0.25},
  {"id": 103, "item_name": "Laptop", "avg_weight": "2kg", "weight_range": "1-3kg", "bbox_ratio": 0.4}
]

**Example Output (note the different weights for T-Shirts):**
[
  {"id": 101, "predicted_weight_value": 130, "predicted_weight_unit": "g"},
  {"id": 102, "predicted_weight_value": 175, "predicted_weight_unit": "g"},
  {"id": 103, "predicted_weight_value": 2.6, "predicted_weight_unit": "kg"}
]
"""

# --------------------------------------------------------------------------
# 2. Gemini API를 직접 호출하는 내부 헬퍼 함수
# --------------------------------------------------------------------------
def _call_gemini_for_weights(items_to_predict: list):
    """Gemini API에 무게 예측을 요청하고 결과를 파싱하여 반환합니다."""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("⚠️ GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
        return None
    
    try:
        genai.configure(api_key=api_key)
        
        generation_config = genai.types.GenerationConfig(response_mime_type="application/json")
        
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',  # 모델명 수정하고 싶으면 해도 됨 pro는 분당 6개 일일25개
            system_instruction=SYSTEM_PROMPT_WEIGHT_PREDICTION,
            generation_config=generation_config
        )

        request_content = json.dumps(items_to_predict, ensure_ascii=False)
        response = model.generate_content(request_content)
        
        return json.loads(response.text)

    except (json.JSONDecodeError, KeyError) as e:
        print(f"[Gemini Service] Failed to parse Gemini JSON response: {e}")
        return None
    except Exception as e:
        print(f"[Gemini Service] An error occurred during weight prediction: {e}")
        return None

# --------------------------------------------------------------------------
# 3. 메인 서비스 함수 (수정 및 개선)
# --------------------------------------------------------------------------
def get_predicted_weights_for_analysis(analysis_id: int):
    """
    특정 분석 ID의 아이템 무게를 가져옵니다.
    - DB에 저장된 예측치가 있으면 그것을 사용합니다.
    - 예측치가 없는 아이템만 API를 통해 예측하고 결과를 DB에 업데이트합니다.
    """
    conn = get_db_connection()
    if not conn:
        return {"error": "Database connection failed."}
        
    try:
        with conn.cursor() as cursor:
            # 1. 분석에 포함된 모든 아이템의 정보를 가져옵니다. (기존 예측치 포함)
            sql = """
                SELECT
                    ai.id, ai.item_name_ko,
                    ai.bbox_x_min, ai.bbox_y_min, ai.bbox_x_max, ai.bbox_y_max,
                    ai.predicted_weight_value, ai.predicted_weight_unit,
                    ar.image_width, ar.image_height,
                    w.weight_range, w.avg_weight_value, w.avg_weight_unit
                FROM analysis_items ai
                JOIN analysis_results ar ON ai.analysis_id = ar.id
                LEFT JOIN items i ON ai.item_name_ko = i.item_name
                LEFT JOIN weights w ON i.id = w.item_id
                WHERE ai.analysis_id = %s;
            """
            cursor.execute(sql, (analysis_id,))
            all_items = cursor.fetchall()

            items_to_predict = []
            already_predicted_items = []

            # 2. 아이템을 '예측 필요'와 '예측 완료' 그룹으로 분리합니다.
            for item in all_items:
                if item['predicted_weight_value'] is None:
                    # 참조 무게 데이터가 없는 아이템은 예측 불가
                    if not item.get('avg_weight_value') or not item.get('weight_range'):
                        continue

                    bbox_width = item['bbox_x_max'] - item['bbox_x_min']
                    bbox_height = item['bbox_y_max'] - item['bbox_y_min']

                    if item['image_width'] and item['image_height'] and item['image_width'] > 0 and item['image_height'] > 0:
                        bbox_ratio = (bbox_width * bbox_height) / (item['image_width'] * item['image_height'])
                    else:
                        bbox_ratio = 0
                    
                    avg_weight_str = f"{item['avg_weight_value']}{item['avg_weight_unit']}"

                    items_to_predict.append({
                        "id": item['id'],
                        "item_name": item['item_name_ko'],
                        "avg_weight": avg_weight_str,
                        "weight_range": item['weight_range'],
                        "bbox_ratio": round(float(bbox_ratio), 4)
                    })
                else:
                    already_predicted_items.append(item)

            # 3. 예측이 필요한 아이템이 있는 경우 API를 호출하고 DB를 업데이트합니다.
            if items_to_predict:
                print(f"[Gemini Service] Predicting weights for {len(items_to_predict)} items for analysis_id: {analysis_id}")
                newly_predicted_weights = _call_gemini_for_weights(items_to_predict)

                if newly_predicted_weights:
                    # 4. API 결과를 DB에 업데이트합니다.
                    update_sql = """
                        UPDATE analysis_items
                        SET predicted_weight_value = %s, predicted_weight_unit = %s
                        WHERE id = %s
                    """
                    update_data = []
                    for pred in newly_predicted_weights:
                        update_data.append(
                            (pred['predicted_weight_value'], pred['predicted_weight_unit'], pred['id'])
                        )
                    
                    cursor.executemany(update_sql, update_data)
                    conn.commit()
                    print(f"[Gemini Service] Successfully updated weights for {len(update_data)} items.")

                    # 5. 전체 결과를 다시 조회하여 최신 상태를 반환합니다.
                    cursor.execute(sql, (analysis_id,))
                    all_items = cursor.fetchall()

            return all_items

    except Exception as e:
        print(f"An error occurred in get_predicted_weights_for_analysis: {e}")
        if conn:
            conn.rollback()
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()
