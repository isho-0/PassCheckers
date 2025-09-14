# backend/models/detected_item_model.py
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

class DetectedItemModel:
    """탐지된 물품을 관리하는 모델 클래스 (PyMySQL 방식)"""
    
    @staticmethod
    def add_item(image_id, item_name, bbox, item_name_EN=None, packing_info='none'):
        """새로운 탐지 아이템을 데이터베이스에 추가합니다."""
        if not all([image_id, item_name, bbox and len(bbox) == 4]):
            raise ValueError("필수 인자(image_id, item_name, bbox)가 누락되었거나 형식이 잘못되었습니다.")

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO detected_items (image_id, item_name_EN, item_name,
                                              bbox_x_min, bbox_y_min, bbox_x_max, bbox_y_max, packing_info)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    image_id, item_name_EN, item_name,
                    bbox[0], bbox[1], bbox[2], bbox[3], packing_info
                ))
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()
    
    @staticmethod
    def delete_items(item_ids):
        """ID 목록을 받아 여러 탐지 아이템을 삭제합니다."""
        if not item_ids:
            return 0
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # IN 절을 사용하여 여러 ID를 한 번에 삭제
                placeholders = ','.join(['%s'] * len(item_ids))
                cursor.execute(f"""
                    DELETE FROM detected_items 
                    WHERE item_id IN ({placeholders})
                """, item_ids)
                conn.commit()
                return cursor.rowcount
        finally:
            conn.close()
    
    @staticmethod
    def get_by_image_id(image_id):
        """특정 이미지 ID에 해당하는 모든 탐지 아이템을 조회합니다."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT item_id, image_id, item_name_EN, item_name,
                           bbox_x_min, bbox_y_min, bbox_x_max, bbox_y_max, packing_info
                    FROM detected_items 
                    WHERE image_id = %s
                    ORDER BY item_id
                """, (image_id,))
                return cursor.fetchall()
        finally:
            conn.close()
    
    @staticmethod
    def get_detailed_by_image_id(image_id):
        """특정 이미지 ID에 대해 탐지된 아이템과 규정 정보를 조인하여 상세 정보를 반환합니다."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        di.item_id, di.image_id, di.item_name_EN, di.item_name,
                        di.bbox_x_min, di.bbox_y_min, di.bbox_x_max, di.bbox_y_max, di.packing_info,
                        i.carry_on_allowed, i.checked_baggage_allowed, i.notes
                    FROM detected_items di
                    LEFT JOIN items i ON di.item_name = i.item_name
                    WHERE di.image_id = %s
                    ORDER BY di.item_id
                """, (image_id,))
                
                results = cursor.fetchall()
                detailed_items = []
                
                for row in results:
                    if row['carry_on_allowed'] is not None:
                        # 규정 정보가 있는 경우
                        item_dict = {
                            'item_id': row['item_id'],
                            'image_id': row['image_id'],
                            'name_ko': row['item_name'],
                            'item_name_EN': row['item_name_EN'],
                            'bbox': [row['bbox_x_min'], row['bbox_y_min'], row['bbox_x_max'], row['bbox_y_max']],
                            'packing_info': row['packing_info'],
                            'carry_on_allowed': row['carry_on_allowed'],
                            'checked_baggage_allowed': row['checked_baggage_allowed'],
                            'notes': row['notes']
                        }
                    else:
                        # 규정 정보가 없는 경우
                        item_dict = {
                            'item_id': row['item_id'],
                            'image_id': row['image_id'],
                            'name_ko': row['item_name'],
                            'item_name_EN': row['item_name_EN'],
                            'bbox': [row['bbox_x_min'], row['bbox_y_min'], row['bbox_x_max'], row['bbox_y_max']],
                            'packing_info': row['packing_info'],
                            'carry_on_allowed': '확인 불가',
                            'checked_baggage_allowed': '확인 불가',
                            'notes': '규정 정보를 찾을 수 없습니다.'
                        }
                    detailed_items.append(item_dict)
                
                return detailed_items
        finally:
            conn.close()

    @staticmethod
    def get_by_id(item_id):
        """ID로 특정 탐지 아이템을 조회합니다."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT item_id, image_id, item_name_EN, item_name,
                           bbox_x_min, bbox_y_min, bbox_x_max, bbox_y_max, packing_info
                    FROM detected_items 
                    WHERE item_id = %s
                """, (item_id,))
                # bbox 값을 리스트로 변환하여 반환
                result = cursor.fetchone()
                if result:
                    result['bbox'] = [result['bbox_x_min'], result['bbox_y_min'], result['bbox_x_max'], result['bbox_y_max']]
                return result
        finally:
            conn.close()

    @staticmethod
    def update_details(item_id, updates):
        """특정 탐지 아이템의 정보를 업데이트합니다."""
        if not updates:
            return 0

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                set_clauses = []
                values = []

                # bbox는 4개의 컬럼으로 분리하여 처리
                if 'bbox' in updates:
                    bbox = updates.pop('bbox')
                    if bbox and len(bbox) == 4:
                        set_clauses.extend([
                            "bbox_x_min = %s",
                            "bbox_y_min = %s",
                            "bbox_x_max = %s",
                            "bbox_y_max = %s"
                        ])
                        values.extend(bbox)
                
                # 나머지 필드 처리
                for key, value in updates.items():
                    # 모델 필드와 DB 컬럼 이름이 다른 경우를 처리 (예: name_ko -> item_name)
                    db_key = 'item_name' if key == 'name_ko' else key
                    set_clauses.append(f"{db_key} = %s")
                    values.append(value)

                if not set_clauses:
                    return 0

                sql = f"""UPDATE detected_items SET {', '.join(set_clauses)} WHERE item_id = %s"""
                values.append(item_id)
                
                cursor.execute(sql, tuple(values))
                conn.commit()
                return cursor.rowcount
        finally:
            conn.close()
    
    @staticmethod
    def to_dict(detected_item):
        """탐지된 아이템 데이터를 딕셔너리로 변환합니다."""
        if not detected_item:
            return None
        return {
            'item_id': detected_item['item_id'],
            'image_id': detected_item['image_id'],
            'name_ko': detected_item['item_name'],
            'item_name_EN': detected_item['item_name_EN'],
            'bbox': [detected_item['bbox_x_min'], detected_item['bbox_y_min'], 
                    detected_item['bbox_x_max'], detected_item['bbox_y_max']],
            'packing_info': detected_item['packing_info']
        }