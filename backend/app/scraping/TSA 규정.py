import requests
from bs4 import BeautifulSoup
import csv
# import mysql.connector   # MySQL 사용 시 필요

def fetch_tsa_data_from_url(url="https://www.tsa.gov/travel/security-screening/whatcanibring/all-list"):
    """TSA 웹사이트에서 데이터를 직접 가져옵니다."""
    try:
        # 웹 브라우저처럼 보이도록 User-Agent 헤더를 추가합니다.
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # 타임아웃을 30초로 늘려 안정성을 높입니다.
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # HTTP 오류가 발생하면 예외를 일으킴
        return response.text
    except requests.RequestException as e:
        print(f"URL에서 데이터를 가져오는 데 실패했습니다: {e}")
        return None

def parse_tsa_html(html_content):
    """HTML 내용을 파싱하여 아이템 목록을 반환합니다."""
    soup = BeautifulSoup(html_content, "html.parser")
    data_list = []

    rows = soup.find_all("tr")  # tr마다 아이템 한 개
    total_rows = len(rows)
    print(f"총 {total_rows}개의 행을 발견했습니다. 파싱을 시작합니다...")

    for i, row in enumerate(rows):
        try:
            # (1) Item
            item_td = row.find("td", {"class": "views-field-nothing"})
            if not item_td:
                continue  # 데이터 없는 행은 건너뛰기

            # 아이템 이름과 링크
            item_tag = item_td.find("a")
            item_name = item_tag.get_text(strip=True) if item_tag else "N/A"
            item_link = item_tag["href"] if item_tag and item_tag.has_attr("href") else ""

            # 아이템 설명
            desc_tag = item_td.find("p")
            description = desc_tag.get_text(strip=True) if desc_tag else ""

            # 설명 안의 링크들
            desc_links = [a["href"] for a in desc_tag.find_all("a", href=True)] if desc_tag else []

            # (2) Carry-on
            carry_td = row.find("td", {"class": "views-field-field-carry-on-baggage"})
            carry_on = carry_td.get_text(strip=True) if carry_td else ""

            # (3) Checked bags
            checked_td = row.find("td", {"class": "views-field-field-checked-baggage"})
            checked_bag = checked_td.get_text(strip=True) if checked_td else ""

            # 리스트에 추가
            data_list.append([
                item_name,
                item_link,
                description,
                ", ".join(desc_links),
                carry_on,
                checked_bag
            ])

            # 50개마다 진행 상황 출력
            if (i + 1) % 50 == 0:
                print(f"진행 상황: {i + 1} / {total_rows} 처리 완료...")

        except Exception as e:
            # 개별 행에서 오류 발생 시, 로그를 남기고 계속 진행
            print(f"오류 발생: {i+1}번째 행({item_name}) 처리 중 문제 발생 - {e}")
            continue
    return data_list

def save_to_csv(data_list, filename="tsa_items.csv"):
    """데이터 리스트를 CSV 파일로 저장합니다."""
    if not data_list:
        print("저장할 데이터가 없습니다.")
        return

    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["Item Name", "Item Link", "Description", "Description Links", "Carry-On Bags", "Checked Bags"])
        writer.writerows(data_list)
    print(f"'{filename}' 저장 완료! 총 {len(data_list)}개의 아이템을 저장했습니다.")

if __name__ == "__main__":
    # 1. 로컬 파일에서 데이터 읽기 (기존 방식)
    # with open("tsa_page.html", "r", encoding="utf-8") as f:
    #     html_content = f.read()

    # 2. 웹에서 직접 데이터 가져오기 (개선된 방식)
    html_content = fetch_tsa_data_from_url()

    if html_content:
        # 3. HTML 파싱
        scraped_data = parse_tsa_html(html_content)
        
        # 4. CSV로 저장
        save_to_csv(scraped_data)
