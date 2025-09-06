import google.generativeai as genai
from config import Config
import re

# API 키를 사용하여 Gemini 클라이언트를 설정합니다.
try:
    genai.configure(api_key=Config.GEMINI_API_KEY)
except Exception as e:
    print(f"[Gemini Service] Failed to configure Gemini: {e}")

# Gemini 모델에게 역할을 부여하고, 응답 규칙을 정의하는 시스템 프롬프트입니다.
SYSTEM_PROMPT = """
You are a helpful assistant for an application that identifies items in luggage and provides their carry-on and checked baggage regulations.
Your task is to provide information about a given item in a specific CSV format.

**Rules:**
1.  You must respond with a single line of comma-separated values (CSV).
2.  The CSV format must be exactly: `Item Name KO,Carry-on Allowed,Checked Baggage Allowed,Notes KO,Item Name EN,Notes EN,Source`
3.  `Item Name KO`: The Korean name of the item I provide.
4.  `Carry-on Allowed`: Must be one of: "예", "아니요", "예 (특별 지침)", "예 (3.4oz/100 ml 이상 또는 동일)". Use your best judgment. For most electronics or valuables, it's "예". For liquids, use the 100ml rule. For sharp objects or weapons, it's "아니요".
5.  `Checked Baggage Allowed`: Must be one of: "예", "아니요", "예 (특별 지침)". Most items are "예" in checked baggage unless they are explosive or dangerous (e.g., most lithium batteries should be carry-on).
6.  `Notes KO`: A brief, one-sentence explanation in Korean.
7.  `Item Name EN`: The English translation of the item name.
8.  `Notes EN`: A brief, one-sentence explanation in English.
9.  `Source`: This must always be the string "API".

**Example Request:**
"안경"

**Example Response:**
안경,예,예,"안경은 개인 필수품으로 기내 및 위탁 수하물 모두 반입이 가능합니다.","Glasses","Glasses are allowed in both carry-on and checked baggage.","API"
"""

def get_item_info_from_gemini(item_name: str):
    """
    Gemini API를 사용하여 새 물품에 대한 규정 정보를 가져옵니다.
    """
    if not item_name:
        return None

    try:
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=SYSTEM_PROMPT
        )
        response = model.generate_content(f'"{item_name}"')

        # Gemini 응답에서 불필요한 공백이나 마크다운을 제거합니다.
        cleaned_text = response.text.strip().replace('`', '')
        
        # CSV 응답을 파싱합니다.
        parts = cleaned_text.split(',')
        if len(parts) != 7:
            print(f"[Gemini Service] Failed to parse Gemini response: {cleaned_text}")
            return None

        # 따옴표로 묶인 설명 부분을 재구성합니다.
        notes_ko = parts[3].strip().strip('"')
        notes_en = parts[5].strip().strip('"')

        return {
            "item_name": parts[0].strip(),
            "carry_on_allowed": parts[1].strip(),
            "checked_baggage_allowed": parts[2].strip(),
            "notes": notes_ko,
            "item_name_EN": parts[4].strip().strip('"'),
            "notes_EN": notes_en,
            "source": parts[6].strip()
        }

    except Exception as e:
        print(f"[Gemini Service] An error occurred: {e}")
        return None
