# backend/db/database_utils.py
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

def fetch_item_info(item_name_en, conn=None):
    """물품 영어 이름으로 DB에서 정보 조회"""
    if conn is None:
        conn = get_db_connection()
        should_close = True
    else:
        should_close = False
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT item_name, item_name_EN, carry_on_allowed, checked_baggage_allowed, notes, notes_EN, source
                FROM items
                WHERE item_name_EN = %s
                LIMIT 1
            """, (item_name_en,))
            return cursor.fetchone()
    finally:
        if should_close:
            conn.close()

def insert_image(user_id, image_bytes, width, height, conn=None):
    """이미지 데이터와 크기를 DB에 저장하고 image_id 반환"""
    if conn is None:
        conn = get_db_connection()
        should_close = True
    else:
        should_close = False
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO images (user_id, image_data, created_at, width, height)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, image_bytes, datetime.now(), width, height))
            if should_close:
                conn.commit()
            return cursor.lastrowid
    finally:
        if should_close:
            conn.close()

def insert_detected_item(image_id, item_name_en, item_name, bbox, conn=None):
    """탐지된 아이템을 DB에 저장"""
    if conn is None:
        conn = get_db_connection()
        should_close = True
    else:
        should_close = False
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO detected_items (image_id, item_name_EN, item_name,
                                          bbox_x_min, bbox_y_min, bbox_x_max, bbox_y_max)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                image_id, item_name_en, item_name,
                bbox[0], bbox[1], bbox[2], bbox[3]
            ))
            if should_close:
                conn.commit()
    finally:
        if should_close:
            conn.close()

def get_image_details_by_id(image_id):
    """ID로 이미지 데이터와 크기를 DB에서 조회"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT image_data, width, height
                FROM images
                WHERE id = %s
                LIMIT 1
            """, (image_id,))
            return cursor.fetchone()
    finally:
        conn.close()
