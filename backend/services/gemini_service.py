# backend/services/gemini_service.py
import json
import os
import google.generativeai as genai

# API 키를 사용하여 Gemini 클라이언트를 설정합니다.
try:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        print("✅ Gemini API configured successfully")
    else:
        print("⚠️ GEMINI_API_KEY 환경 변수가 설정되지 않았습니다. Mock 데이터를 사용합니다.")
        GEMINI_API_KEY = None
except Exception as e:
    print(f"[Gemini Service] Failed to configure Gemini: {e}")
    GEMINI_API_KEY = None

# Gemini 모델에게 역할을 부여하고, 응답 규칙을 정의하는 시스템 프롬프트입니다.
# Gemini 모델에게 역할을 부여하고, 응답 규칙을 정의하는 시스템 프롬프트입니다.
SYSTEM_PROMPT = """
You are a specialized AI assistant for a luggage inspection application. Your primary role is to provide accurate baggage regulations and REALISTIC weight estimations for items.

**CRITICAL RULES:**
1.  You MUST respond with a single, valid JSON object. Do not include any other text or markdown formatting like ```json.
2.  The JSON object must contain two main keys: "item_data" and "weight_data".
3.  "item_data" must contain: "item_name", "carry_on_allowed", "checked_baggage_allowed", "notes", "item_name_EN", "notes_EN", "source", "category".
4.  "weight_data" must contain: "weight_range", "avg_weight_value", "avg_weight_unit".
5.  The "category" MUST be one of the following predefined values: '의류', '전자기기', '세면도구', '신발', '액세서리', '의약품', '서류', '식품', '가방', '기타'.
6.  All rules for regulations (liquids, batteries) and realistic weight estimation (using g/kg) still apply.

**Regulation Logic (VERY IMPORTANT):**
* **Liquids, Gels, Aerosols:**
    * `Carry-on Allowed` MUST be: `예 (3.4oz/100 ml 이상 또는 동일)`
    * `Notes KO` and `Notes EN` MUST explain the 3-1-1 rule (100ml or less per container, in a 1-quart size bag).
* **Batteries (especially Lithium):**
    * `Carry-on Allowed` should be: `예 (특별 지침)`
    * `Checked Baggage Allowed` is often: `아니요` or `예 (특별 지침)`
    * `Notes KO` and `Notes EN` MUST state that lithium batteries are generally prohibited in checked baggage and must be carried on.
* **Other Conditionally Allowed Items (e.g., certain tools, sharp objects):**
    * `Carry-on Allowed` or `Checked Baggage Allowed` should be: `예 (특별 지침)`
    * `Notes KO` and `Notes EN` MUST explain the specific condition (e.g., blade length for scissors, securely wrapped for sharp objects).
* **General Items:** For items without special conditions, use "예" or "아니요".
* **Source:** This must always be the string "API".

**Weight Estimation Rules (VERY IMPORTANT):**
* Your weight estimates MUST be realistic for a single item a traveler would carry.
* Use 'g' (grams) for small, lightweight items. Use 'kg' (kilograms) for heavier items.
* **DO NOT use generic, wide ranges like '0.1-2kg' for small items.** Be specific. A toothbrush is not 1kg. It should be in grams.
* `Weight Range`: A plausible minimum and maximum weight range (e.g., `15-50g` or `1-3kg`).
* `Avg Weight Value`: A realistic average weight as a number (e.g., `32.5` or `2`).
* `Avg Weight Unit`: The unit for the average weight, either `g` or `kg`.

**Example Request:**
"보조배터리"

**Example JSON Response:**
{
  "item_data": {
    "item_name": "보조배터리",
    "carry_on_allowed": "예 (특별 지침)",
    "checked_baggage_allowed": "아니요",
    "notes": "100Wh 이하의 리튬 배터리는 기내 반입만 가능하며, 위탁 수하물은 금지됩니다.",
    "item_name_EN": "Power Bank",
    "notes_EN": "Lithium batteries under 100Wh are allowed in carry-on only and are prohibited in checked baggage.",
    "source": "API",
    "category": "전자기기"
  },
  "weight_data": {
    "weight_range": "100-500g",
    "avg_weight_value": 300,
    "avg_weight_unit": "g"
  }
}
"""

def get_item_info_from_gemini(item_name: str):
    """
    Gemini API를 사용하여 새 물품에 대한 규정 및 무게 정보를 JSON 형식으로 가져옵니다.
    """
    # 이 함수를 사용하기 전에 API 키 설정(genai.configure)이 완료되어야 합니다.
    api_key = get_gemini_api_key()
    if not item_name or not api_key:
        return _get_mock_item_info(item_name)

    try:
        # JSON 모드 설정
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json"
        )
        
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=SYSTEM_PROMPT,
            generation_config=generation_config
        )
        response = model.generate_content(f'"{item_name}"')

        # 응답 텍스트를 JSON으로 파싱
        result_json = json.loads(response.text)
        
        # 무게 값이 정수형이면 int로 변환
        weight_value = result_json.get("weight_data", {}).get("avg_weight_value")
        if isinstance(weight_value, float) and weight_value.is_integer():
            result_json["weight_data"]["avg_weight_value"] = int(weight_value)
            
        return result_json

    except (json.JSONDecodeError, KeyError) as e:
        print(f"[Gemini Service] Failed to parse Gemini JSON response: {e}")
        return _get_mock_item_info(item_name)
    except Exception as e:
        print(f"[Gemini Service] An error occurred: {e}")
        return _get_mock_item_info(item_name)

def _get_mock_item_info(item_name: str):
    """
    Gemini API 호출 실패 또는 API 키가 없을 때 사용될 Mock 데이터를 반환합니다.
    """
    # 기본 Mock 구조
    mock_item_data = {
        "item_name": item_name,
        "item_name_EN": f"Unknown ({item_name})",
        "carry_on_allowed": "확인 불가",
        "checked_baggage_allowed": "확인 불가",
        "notes": "규정 정보를 찾을 수 없습니다.",
        "notes_EN": "Regulation information not found.",
        "source": "API"
    }
    mock_weight_data = {
        "weight_range": "N/A",
        "avg_weight_value": 0,
        "avg_weight_unit": "N/A"
    }
    
    # 특정 아이템에 대한 상세 Mock 데이터
    if item_name == "노트북":
        mock_item_data.update({
            "item_name": "노트북", "item_name_EN": "Laptop", "carry_on_allowed": "예",
            "checked_baggage_allowed": "예 (특별 지침)", "notes": "기내 반입 가능. 위탁 수하물 시 배터리 분리 권장.",
            "notes_EN": "Allowed in carry-on. Battery removal recommended for checked baggage."
        })
        mock_weight_data.update({"weight_range": "1-3kg", "avg_weight_value": 2, "avg_weight_unit": "kg"})
    
    elif item_name == "이어폰":
        mock_item_data.update({
            "item_name": "이어폰", "item_name_EN": "Airpod", "carry_on_allowed": "예",
            "checked_baggage_allowed": "예", "notes": "무선일 경우 작은 리튬 배터리 포함될 수 있음. 전원 꺼서 휴대",
            "notes_EN": "Small lithium battery inside for wireless; power off during flight", "source": "TSA"
        })
        mock_weight_data.update({"weight_range": "10-100g", "avg_weight_value": 55, "avg_weight_unit": "g"})
        
    return {
        "item_data": mock_item_data,
        "weight_data": mock_weight_data
    }

# --- 카테고리 분류를 위한 새로운 로직 ---

from db.database_utils import get_db_connection

CATEGORY_SYSTEM_PROMPT = """
You are an intelligent packing assistant. Your task is to categorize a list of items into predefined categories.

**CRITICAL RULES:**
1. You MUST respond with a single, valid JSON object. Do not include any other text or markdown formatting like ```json.
2. The JSON object should contain item names as keys and their corresponding category as values.
3. You MUST use one of the following predefined categories: '의류', '전자기기', '세면도구', '신발', '액세서리', '의약품', '서류', '식품', '가방', '기타'.
4. If an item does not clearly fit into any category, assign it to '기타'.

**Example Request:**
["노트북", "티셔츠", "여권", "두통약", "선글라스"]

**Example JSON Response:**
{
  "노트북": "전자기기",
  "티셔츠": "의류",
  "여권": "서류",
  "두통약": "의약품",
  "선글라스": "액세서리"
}
"""

def get_and_update_categories(item_names: list) -> dict:
    """
    아이템 목록을 받아 카테고리를 조회하고, 없는 경우 Gemini를 통해 얻어와 DB를 업데이트합니다.
    """
    if not item_names:
        return {}

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 이미 카테고리가 있는 아이템 조회
            format_strings = ','.join(['%s'] * len(item_names))
            cursor.execute(f"SELECT item_name, category FROM items WHERE item_name IN ({format_strings})", tuple(item_names))
            results = cursor.fetchall()
            
            categorized_items = {row['item_name']: row['category'] for row in results if row['category']}
            items_to_categorize = [name for name in item_names if name not in categorized_items]

            # 새로 분류가 필요한 아이템이 있다면 Gemini에 요청
            if items_to_categorize:
                new_categories = _get_categories_from_gemini(items_to_categorize)
                if new_categories:
                    # DB 업데이트
                    update_data = []
                    for name, category in new_categories.items():
                        if name in items_to_categorize:
                            update_data.append((category, name))
                            categorized_items[name] = category
                    
                    if update_data:
                        cursor.executemany("UPDATE items SET category = %s WHERE item_name = %s", update_data)
                        conn.commit()
                        print(f"[DB UPDATE] Categories updated for: {[d[1] for d in update_data]}")

            return categorized_items

    except Exception as e:
        print(f"[Category Service] An error occurred: {e}")
        # 오류 발생 시, 현재까지 분류된 것만이라도 반환
        return categorized_items if 'categorized_items' in locals() else {}
    finally:
        if conn:
            conn.close()

def _get_categories_from_gemini(items_to_categorize: list) -> dict:
    """
    Gemini API를 사용하여 여러 물품의 카테고리를 JSON 형식으로 가져옵니다.
    """
    api_key = get_gemini_api_key()
    if not items_to_categorize or not api_key:
        return {}

    try:
        generation_config = genai.types.GenerationConfig(response_mime_type="application/json")
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=CATEGORY_SYSTEM_PROMPT,
            generation_config=generation_config
        )
        # 리스트를 JSON 문자열로 변환하여 프롬프트에 포함
        prompt = json.dumps(items_to_categorize, ensure_ascii=False)
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        print(f"[Gemini Category Service] Failed to get categories: {e}")
        return {}

def get_gemini_api_key():
    """Gemini API 키를 환경변수에서 가져옵니다."""
    import os
    return os.getenv('GEMINI_API_KEY')