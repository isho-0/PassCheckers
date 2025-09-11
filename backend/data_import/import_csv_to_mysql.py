#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
수하물 규정 CSV 파일을 MySQL 데이터베이스에 저장하는 스크립트
"""

import pandas as pd
import pymysql
import os
import sys
from datetime import datetime
from urllib.parse import urlparse

# 상위 디렉토리의 config 모듈 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

def get_db_connection():
    """데이터베이스 연결을 생성합니다."""
    url = os.environ.get('DATABASE_URL')
    if url is None:
        url = Config.SQLALCHEMY_DATABASE_URI

    # SQLAlchemy의 URI 형식을 urlparse가 이해할 수 있도록 변경
    if 'mysql+pymysql://' in url:
        url = url.replace('mysql+pymysql://', 'mysql://')

    parsed = urlparse(url)
    return pymysql.connect(
        host=parsed.hostname,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path.lstrip('/'),
        port=parsed.port or 3306,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def create_sample_csv():
    """샘플 수하물 규정 CSV 파일을 생성합니다."""
    sample_data = [
        {
            'item_name': '노트북',
            'item_name_EN': 'Laptop',
            'carry_on_allowed': '예',
            'checked_baggage_allowed': '예',
            'notes': '노트북은 기내 및 위탁 수하물 모두 반입 가능합니다. 기내 반입 시 보안 검색에서 별도 검사를 받을 수 있습니다.',
            'notes_EN': 'Laptops are allowed in both carry-on and checked baggage. They may require separate screening at security checkpoints.',
            'source': 'manual'
        },
        {
            'item_name': '액체류',
            'item_name_EN': 'Liquids',
            'carry_on_allowed': '예 (3.4oz/100 ml 이상 또는 동일)',
            'checked_baggage_allowed': '예',
            'notes': '기내 반입 시 100ml 이하 용기에 담아 1리터 비닐봉지에 넣어야 합니다.',
            'notes_EN': 'Must be in containers of 100ml or less and placed in a 1-liter plastic bag for carry-on.',
            'source': 'manual'
        },
        {
            'item_name': '칼',
            'item_name_EN': 'Knives',
            'carry_on_allowed': '아니요',
            'checked_baggage_allowed': '예 (특별 지침)',
            'notes': '칼은 기내 반입이 금지되며, 위탁 수하물에만 반입 가능합니다.',
            'notes_EN': 'Knives are prohibited in carry-on baggage and only allowed in checked baggage.',
            'source': 'manual'
        },
        {
            'item_name': '담배',
            'item_name_EN': 'Cigarettes',
            'carry_on_allowed': '예',
            'checked_baggage_allowed': '예',
            'notes': '담배는 기내 및 위탁 수하물 모두 반입 가능하지만, 목적지 국가의 규정을 확인해야 합니다.',
            'notes_EN': 'Cigarettes are allowed in both carry-on and checked baggage, but check destination country regulations.',
            'source': 'manual'
        },
        {
            'item_name': '가방',
            'item_name_EN': 'General Bag',
            'carry_on_allowed': '예',
            'checked_baggage_allowed': '예',
            'notes': '일반 가방은 기내 및 위탁 수하물 모두 반입 가능합니다.',
            'notes_EN': 'General bags are allowed in both carry-on and checked baggage.',
            'source': 'manual'
        },
        {
            'item_name': '튜브',
            'item_name_EN': 'Tube (Liquid)',
            'carry_on_allowed': '예 (3.4oz/100 ml 이상 또는 동일)',
            'checked_baggage_allowed': '예',
            'notes': '액체가 들어있는 튜브는 100ml 이하로 제한됩니다.',
            'notes_EN': 'Tubes containing liquids are limited to 100ml or less.',
            'source': 'manual'
        },
        {
            'item_name': '병',
            'item_name_EN': 'Bottle',
            'carry_on_allowed': '예 (3.4oz/100 ml 이상 또는 동일)',
            'checked_baggage_allowed': '예',
            'notes': '액체가 들어있는 병은 100ml 이하로 제한됩니다.',
            'notes_EN': 'Bottles containing liquids are limited to 100ml or less.',
            'source': 'manual'
        },
        {
            'item_name': '가위',
            'item_name_EN': 'Scissors',
            'carry_on_allowed': '아니요',
            'checked_baggage_allowed': '예 (특별 지침)',
            'notes': '가위는 기내 반입이 금지되며, 위탁 수하물에만 반입 가능합니다.',
            'notes_EN': 'Scissors are prohibited in carry-on baggage and only allowed in checked baggage.',
            'source': 'manual'
        },
        {
            'item_name': '쌈장',
            'item_name_EN': 'Sauce (Fermented Paste)',
            'carry_on_allowed': '예 (3.4oz/100 ml 이상 또는 동일)',
            'checked_baggage_allowed': '예',
            'notes': '발효된 페이스트류는 100ml 이하로 제한됩니다.',
            'notes_EN': 'Fermented paste products are limited to 100ml or less.',
            'source': 'manual'
        }
    ]
    
    df = pd.DataFrame(sample_data)
    csv_path = os.path.join(os.path.dirname(__file__), 'luggage_regulations.csv')
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"샘플 CSV 파일이 생성되었습니다: {csv_path}")
    return csv_path

def import_csv_to_mysql(csv_file_path):
    """CSV 파일을 MySQL 데이터베이스에 저장합니다."""
    try:
        # CSV 파일 읽기
        df = pd.read_csv(csv_file_path, encoding='utf-8-sig')
        print(f"CSV 파일을 읽었습니다: {len(df)}개 행")
        
        # 데이터베이스 연결
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 기존 데이터 삭제 (선택사항)
        clear_existing = input("기존 데이터를 삭제하고 새로 시작하시겠습니까? (y/N): ").lower() == 'y'
        if clear_existing:
            cursor.execute("DELETE FROM items")
            print("기존 데이터가 삭제되었습니다.")
        
        # 데이터 삽입
        insert_count = 0
        for index, row in df.iterrows():
            try:
                # NULL 값 처리
                item_name = row['item_name'] if pd.notna(row['item_name']) else ''
                item_name_en = row['item_name_EN'] if pd.notna(row['item_name_EN']) else ''
                carry_on_allowed = row['carry_on_allowed'] if pd.notna(row['carry_on_allowed']) else ''
                checked_baggage_allowed = row['checked_baggage_allowed'] if pd.notna(row['checked_baggage_allowed']) else ''
                notes = row['notes'] if pd.notna(row['notes']) else ''
                notes_en = row['notes_EN'] if pd.notna(row['notes_EN']) else ''
                source = row['source'] if pd.notna(row['source']) else 'TSA'
                
                cursor.execute("""
                    INSERT INTO items (item_name, item_name_EN, carry_on_allowed, 
                                     checked_baggage_allowed, notes, notes_EN, source)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    item_name,
                    item_name_en,
                    carry_on_allowed,
                    checked_baggage_allowed,
                    notes,
                    notes_en,
                    source
                ))
                insert_count += 1
                print(f"삽입됨: {item_name} ({item_name_en})")
            except Exception as e:
                print(f"오류 - {row['item_name']}: {e}")
                continue
        
        # 변경사항 커밋
        conn.commit()
        print(f"\n총 {insert_count}개 항목이 데이터베이스에 저장되었습니다.")
        
        # 최종 확인
        cursor.execute("SELECT COUNT(*) as total FROM items")
        total_count = cursor.fetchone()['total']
        print(f"데이터베이스의 총 항목 수: {total_count}")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """메인 함수"""
    print("=== 수하물 규정 CSV → MySQL 가져오기 ===")
    
    # TSA CSV 파일 경로 확인
    tsa_csv_file = os.path.join(os.path.dirname(__file__), 'tsa_items_trans.csv')
    sample_csv_file = os.path.join(os.path.dirname(__file__), 'luggage_regulations.csv')
    
    if os.path.exists(tsa_csv_file):
        print(f"TSA 규정 CSV 파일을 발견했습니다: {tsa_csv_file}")
        csv_file = tsa_csv_file
    elif os.path.exists(sample_csv_file):
        print(f"샘플 CSV 파일을 발견했습니다: {sample_csv_file}")
        csv_file = sample_csv_file
    else:
        print("CSV 파일이 없습니다. 샘플 파일을 생성합니다...")
        csv_file = create_sample_csv()
    
    # CSV 파일을 MySQL에 가져오기
    import_csv_to_mysql(csv_file)

if __name__ == "__main__":
    main()
