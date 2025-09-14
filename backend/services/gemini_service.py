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
SYSTEM_PROMPT = """
You are a specialized AI assistant for a luggage inspection application. Your primary role is to provide accurate baggage regulations and REALISTIC weight estimations for items.

**CRITICAL RULES:**
1.  You MUST respond with a single, valid JSON object. Do not include any other text or markdown formatting like ```json.
2.  The JSON object must contain two main keys: "item_data" and "weight_data".
3.  "item_data" must contain: "item_name", "carry_on_allowed", "checked_baggage_allowed", "notes", "item_name_EN", "notes_EN", "source".
4.  "weight_data" must contain: "weight_range", "avg_weight_value", "avg_weight_unit".
5.  All rules for regulations (liquids, batteries) and realistic weight estimation (using g/kg) still apply.

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
    "source": "API"
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

def get_gemini_api_key():
    """Gemini API 키를 환경변수에서 가져옵니다."""
    import os
    return os.getenv('GEMINI_API_KEY')