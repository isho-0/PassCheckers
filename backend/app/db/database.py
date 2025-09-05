from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# app/db/database.py
import pandas as pd
from sqlalchemy import create_engine, exc, text
from datetime import datetime
from config import Config
import pymysql
import os
from urllib.parse import urlparse

def get_engine():
    """
    DB 연결 엔진 생성
    """
    try:
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        return engine
    except exc.SQLAlchemyError as e:
        print(f"[DB ERROR] {e}")
        return None

def get_db_connection():
    """
    PyMySQL 연결을 생성하여 반환합니다.
    환경 변수 'DATABASE_URL'이 있으면 사용하고, 없으면 config 파일의 값을 사용합니다.
    """
    url = os.environ.get('DATABASE_URL')
    if url is None:
        url = Config.SQLALCHEMY_DATABASE_URI

    # SQLAlchemy의 URI 형식(mysql+pymysql://)을 urlparse가 이해할 수 있도록 변경
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

def fetch_item_info(item_name_en: str):
    """
    물품 영어 이름으로 DB에서 정보 조회
    """
    engine = get_engine()
    if not engine:
        return None

    try:
        query = text("""
            SELECT item_name, item_name_EN, carry_on_allowed, checked_baggage_allowed, notes
            FROM items
            WHERE item_name_EN = :item_name_en
            LIMIT 1
        """)
        with engine.connect() as conn:
            result = conn.execute(query, {"item_name_en": item_name_en}).mappings().fetchone()
            if result:
                return dict(result)
            else:
                return None
    except Exception as e:
        print(f"[DB QUERY ERROR] {e}")
        return None


# --- 이미지 저장 ---
def insert_image(conn, user_id: str, image_bytes: bytes, width: int, height: int):
    """
    이미지 데이터와 크기를 DB에 저장하고 image_id 반환.
    """
    image_query = text("""
        INSERT INTO images (user_id, image_data, created_at, width, height)
        VALUES (:user_id, :image_data, :created_at, :width, :height)
    """)
    result = conn.execute(image_query, {
        "user_id": user_id,
        "image_data": image_bytes,
        "created_at": datetime.now(),
        "width": width,
        "height": height
    })
    return result.lastrowid


# --- 탐지된 아이템 저장 ---
def insert_detected_item(conn, image_id: int, item_name_en: str, item_name: str, bbox: list):
    """
    탐지된 아이템을 DB에 저장.
    """
    insert_query = text("""
        INSERT INTO detected_items (image_id, item_name_EN, item_name,
                                    bbox_x_min, bbox_y_min, bbox_x_max, bbox_y_max)
        VALUES (:image_id, :item_name_en, :item_name, :bbox_x_min, :bbox_y_min, :bbox_x_max, :bbox_y_max)
    """)
    conn.execute(insert_query, {
        "image_id": image_id,
        "item_name_en": item_name_en,
        "item_name": item_name,
        "bbox_x_min": bbox[0],
        "bbox_y_min": bbox[1],
        "bbox_x_max": bbox[2],
        "bbox_y_max": bbox[3]
    })


def get_image_details_by_id(image_id: int):
    """
    ID로 이미지 데이터와 크기를 DB에서 조회합니다.
    """
    engine = get_engine()
    if not engine:
        return None

    try:
        query = text("""
            SELECT image_data, width, height
            FROM images
            WHERE id = :image_id
            LIMIT 1
        """)
        with engine.connect() as conn:
            result = conn.execute(query, {"image_id": image_id}).mappings().fetchone()
            if result:
                return dict(result)
            else:
                return None
    except Exception as e:
        print(f"[DB QUERY ERROR] {e}")
        return None