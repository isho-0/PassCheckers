# backend/services/gemini_predict.py
import os
import json
import google.generativeai as genai
from db.database_utils import get_db_connection

# --------------------------------------------------------------------------
# 1. Gemini API 호출을 위한 시스템 프롬프트
# --------------------------------------------------------------------------
SYSTEM_PROMPT_WEIGHT_PREDICTION = """
You are an expert AI specializing in estimating the weight of objects found in luggage, based on visual and reference data.

Your task is to predict the final weight for a list of items provided in a JSON array.

**Input Data Schema (for each item):**
- `id`: The unique identifier for the specific item in an analysis.
- `item_name`: The name of the item.
- `avg_weight`: The average or reference weight of this item type, as a string including its unit (e.g., "350g" or "3.5kg"). This is your primary baseline.
- `weight_range`: The typical weight range for this item type (e.g., "200-500g"). Your final prediction should plausibly fall within or near this range.
- `bbox_ratio`: A decimal representing the item's detected bounding box area relative to the total image area. A larger ratio suggests the item appears larger in the image.

**Reasoning Logic:**
1.  Use the `avg_weight` as the starting baseline for your prediction.
2.  Critically analyze the `bbox_ratio`. A very large ratio for an item that is typically small (like a lipstick) might indicate it's just close to the camera, not necessarily heavier. A large ratio for an item that varies in size (like a laptop) might indicate it's a larger model.
3.  Adjust the baseline weight up or down based on your reasoning about the `bbox_ratio` and your real-world knowledge of the item.
4.  The final `predicted_weight_value` must be a number, and `predicted_weight_unit` must be either "g" or "kg".

**Output Format Rules:**
- You MUST respond ONLY with a valid JSON array.
- Do not include any other text, explanations, or markdown formatting like ```json.
- Each object in the array must follow this exact structure:
  `{"id": <number>, "predicted_weight_value": <number>, "predicted_weight_unit": "<'g' or 'kg'>"}`

**Example Input:**
[
  {"id": 45, "item_name": "Lipstick", "avg_weight": "20g", "weight_range": "10-30g", "bbox_ratio": 0.25},
  {"id": 88, "item_name": "Laptop", "avg_weight": "2kg", "weight_range": "1-3kg", "bbox_ratio": 0.4}
]

**Example Output:**
[
  {"id": 45, "predicted_weight_value": 22, "predicted_weight_unit": "g"},
  {"id": 88, "predicted_weight_value": 2.6, "predicted_weight_unit": "kg"}
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
            model_name='gemini-1.5-flash',  # 모델명 수정
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
