# backend/models/item_model.py
import pymysql
from datetime import datetime
from config import Config
import os
from urllib.parse import urlparse

def get_db_connection():
    """PyMySQL 연결을 생성하여 반환합니다."""
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

class ItemModel:
    """물품 정보를 관리하는 모델 클래스 (PyMySQL 방식)"""
    
    @staticmethod
    def get_by_name(item_name):
        """이름으로 특정 아이템의 상세 정보를 조회합니다."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, item_name, item_name_EN, carry_on_allowed, 
                           checked_baggage_allowed, notes, notes_EN, source
                    FROM items 
                    WHERE item_name = %s
                """, (item_name,))
                return cursor.fetchone()
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(item_id):
        """ID로 특정 아이템의 상세 정보를 조회합니다."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, item_name, item_name_EN, carry_on_allowed, 
                           checked_baggage_allowed, notes, notes_EN, source
                    FROM items 
                    WHERE id = %s
                """, (item_id,))
                return cursor.fetchone()
        finally:
            conn.close()
    
    @staticmethod
    def get_all_details():
        """프론트엔드에서 사용할 모든 아이템 상세 정보를 조회합니다."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, item_name, item_name_EN, carry_on_allowed, 
                           checked_baggage_allowed, notes, notes_EN, source
                    FROM items
                    ORDER BY item_name
                """)
                return cursor.fetchall()
        finally:
            conn.close()
    
    @staticmethod
    def get_all_for_caching():
        """매칭 서비스 캐싱을 위해 id와 이름만 조회합니다."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, item_name
                    FROM items
                    ORDER BY item_name
                """)
                return cursor.fetchall()
        finally:
            conn.close()
    
    @staticmethod
    def add_item_from_api(item_data, weight_data):
        """API (Gemini)로부터 받은 데이터를 기반으로 새 아이템과 무게 정보를 추가합니다."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 1. items 테이블에 데이터 추가
                # 데이터 유효성 검사 및 기본값 설정
                carry_on = item_data.get('carry_on_allowed', '아니요')
                checked = item_data.get('checked_baggage_allowed', '아니요')
                
                # 허용된 값 목록 (더 유연하게 startswith로 체크)
                allowed_carry_on_prefixes = ["예", "아니요"]
                allowed_checked_prefixes = ["예", "아니요"]

                if not any(carry_on.startswith(prefix) for prefix in allowed_carry_on_prefixes):
                    carry_on = '아니요'
                if not any(checked.startswith(prefix) for prefix in allowed_checked_prefixes):
                    checked = '아니요'

                cursor.execute("""
                    INSERT INTO items (item_name, item_name_EN, carry_on_allowed, 
                                     checked_baggage_allowed, notes, notes_EN, source, category)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    item_data['item_name'],
                    item_data.get('item_name_EN'),
                    carry_on,
                    checked,
                    item_data.get('notes'),
                    item_data.get('notes_EN'),
                    'API',
                    item_data.get('category') # 새로 추가된 카테고리 필드
                ))
                
                # 새로 추가된 item의 ID 가져오기
                new_item_id = cursor.lastrowid
                
                # 2. weights 테이블 생성 (없을 경우)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `weights` (
                      `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                      `item_id` INT NOT NULL UNIQUE,
                      `weight_range` VARCHAR(255) COLLATE utf8mb4_unicode_ci,
                      `avg_weight_value` DECIMAL(10, 2),
                      `avg_weight_unit` VARCHAR(10) COLLATE utf8mb4_unicode_ci,
                      CONSTRAINT `fk_item_id` FOREIGN KEY (`item_id`) 
                      REFERENCES `items` (`id`) 
                      ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """)

                # 3. weights 테이블에 데이터 추가
                cursor.execute("""
                    INSERT INTO weights (item_id, weight_range, avg_weight_value, avg_weight_unit)
                    VALUES (%s, %s, %s, %s)
                """, (
                    new_item_id,
                    weight_data.get('weight_range'),
                    weight_data.get('avg_weight_value'),
                    weight_data.get('avg_weight_unit')
                ))

                # 모든 변경사항을 커밋
                conn.commit()
                
                # 4. 추가된 아이템의 전체 정보를 다시 조회하여 반환
                cursor.execute("""
                    SELECT id, item_name, item_name_EN, carry_on_allowed, 
                           checked_baggage_allowed, notes, notes_EN, source
                    FROM items 
                    WHERE id = %s
                """, (new_item_id,))
                return cursor.fetchone()

        except Exception as e:
            conn.rollback() # 오류 발생 시 롤백
            print(f"[ItemModel] Error in add_item_from_api: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def to_dict(item):
        """아이템 데이터를 딕셔너리로 변환합니다."""
        if not item:
            return None
        return {
            'id': item['id'],
            'item_name': item['item_name'],
            'item_name_EN': item['item_name_EN'],
            'carry_on_allowed': item['carry_on_allowed'],
            'checked_baggage_allowed': item['checked_baggage_allowed'],
            'notes': item['notes'],
            'notes_EN': item['notes_EN'],
            'source': item['source']
        }