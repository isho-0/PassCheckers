# backend/routes/locations.py
from flask import Blueprint, request, jsonify
from db.database_utils import get_db_connection

locations_bp = Blueprint('locations_bp', __name__, url_prefix='/api/locations')

@locations_bp.route('/continents', methods=['GET'])
def get_continents():
    """DB에서 고유한 대륙 목록을 가져와 반환합니다."""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT continent_ko FROM locations WHERE continent_ko IS NOT NULL ORDER BY continent_ko")
            continents = [row['continent_ko'] for row in cursor.fetchall()]
        return jsonify(continents)
    except Exception as e:
        print(f"Error fetching continents: {e}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500
    finally:
        if conn:
            conn.close()

@locations_bp.route('/countries', methods=['GET'])
def get_countries():
    """특정 대륙에 속한 국가 목록을 반환합니다."""
    continent = request.args.get('continent')
    if not continent:
        return jsonify({"error": "'continent' 쿼리 파라미터가 필요합니다."}), 400

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT country_ko, location_id 
                FROM locations 
                WHERE continent_ko = %s AND location_type = 'country' 
                ORDER BY country_ko
            """, (continent,))
            countries = cursor.fetchall()
        return jsonify(countries)
    except Exception as e:
        print(f"Error fetching countries for continent {continent}: {e}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500
    finally:
        if conn:
            conn.close()
