import csv
import time
import os

# 번역 라이브러리 임포트
try:
    from deep_translator import GoogleTranslator
except ImportError:
    print("번역을 위해 'deep-translator' 라이브러리가 필요합니다.")
    print("터미널에서 'pip install deep-translator' 명령어를 실행해 설치해주세요.")
    print("기존 googletrans 라이브러리는 'pip uninstall googletrans'로 삭제하는 것을 권장합니다.")
    exit()

def translate_text_with_retry(translator, text, retries=3, delay=2):
    """
    텍스트 번역을 시도하고, 실패 시 몇 차례 재시도합니다.
    """
    if not text or not text.strip():
        return ""  # 비어있는 텍스트는 번역하지 않고 반환

    for attempt in range(retries):
        try:
            # API에 과도한 요청을 보내지 않도록 약간의 지연 시간을 둡니다.
            #time.sleep(0.1)
            translated_text = translator.translate(text)
            # 번역 결과가 None일 경우 원본 텍스트 반환
            return translated_text if translated_text is not None else text
        except Exception as e:
            print(f"번역 오류: '{text[:20]}...' 재시도 중... ({attempt + 1}/{retries}) - {e}")
            #if attempt < retries - 1:
                #time.sleep(delay * (attempt + 1)) # 재시도 간격을 점차 늘림
    
    print(f"번역 최종 실패: '{text[:20]}...' 원본 텍스트를 반환합니다.")
    return text # 모든 재시도 실패 시 원본 텍스트 반환

def run_csv_translation(input_filepath, output_filepath):
    """
    입력받은 CSV 파일을 읽어 내용을 한국어로 번역한 후, 새로운 CSV 파일로 저장합니다.
    """
    if not os.path.exists(input_filepath):
        print(f"오류: 입력 파일 '{input_filepath}'을(를) 찾을 수 없습니다.")
        print("스크래핑 스크립트(TSA 규정.py)를 먼저 실행하여 'tsa_items.csv' 파일을 생성했는지 확인해주세요.")
        return

    translator = GoogleTranslator(source='en', target='ko')
    
    try:
        with open(input_filepath, mode='r', encoding='utf-8-sig') as infile:
            reader = list(csv.reader(infile))
    except Exception as e:
        print(f"파일을 읽는 중 오류가 발생했습니다: {e}")
        return

    # 원본 CSV 파일의 헤더가 2줄(한글, 영어)인 것을 가정하고 건너뜁니다.
    if len(reader) < 3:
        print("오류: 파일에 데이터가 충분하지 않습니다. (헤더 포함 최소 3줄 필요)")
        return
        
    data_rows = reader[2:]
    total_rows = len(data_rows)
    
    print(f"총 {total_rows}개 항목의 번역을 시작합니다...")

    with open(output_filepath, mode='w', newline='', encoding='utf-8-sig') as outfile:
        writer = csv.writer(outfile)

        # 번역된 내용만 저장할 것이므로, 한글 헤더를 작성합니다.
        new_headers = [
            "물품명", "설명", "휴대 수하물", "위탁 수하물"
        ]
        writer.writerow(new_headers)

        # 데이터 행을 순회하며 번역 및 저장
        for i, row in enumerate(data_rows):
            if len(row) < 6:
                print(f"경고: {i+1}번째 행의 데이터가 부족하여 건너뜁니다: {row}")
                continue
                
            # 번역할 원본 영어 텍스트
            item_name_en = row[0]       # Item Name
            description_en = row[2]     # Description
            carry_on_en = row[4]        # Carry-On Bags
            checked_bag_en = row[5]     # Checked Bags

            print(f"번역 중 ({i + 1}/{total_rows}): {item_name_en}")

            # 4개 필드 모두 번역
            item_name_ko = translate_text_with_retry(translator, item_name_en)
            description_ko = translate_text_with_retry(translator, description_en)
            carry_on_ko = translate_text_with_retry(translator, carry_on_en)
            checked_bag_ko = translate_text_with_retry(translator, checked_bag_en)

            # 번역된 결과만 새로운 행으로 구성
            new_row = [item_name_ko, description_ko, carry_on_ko, checked_bag_ko]
            writer.writerow(new_row)

    print(f"\n번역 완료! '{output_filepath}' 파일에 성공적으로 저장되었습니다.")

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, '..', '..'))

    input_csv = os.path.join(project_root, 'tsa_items.csv')
    output_csv = os.path.join(project_root, 'tsa_items_translated.csv')

    run_csv_translation(input_csv, output_csv)