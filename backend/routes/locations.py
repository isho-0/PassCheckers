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
            continents_ko = [row['continent_ko'] for row in cursor.fetchall()]
            continents = [{'continent_id': name, 'continent_ko': name} for name in continents_ko]
        return jsonify(continents)
    except Exception as e:
        print(f"Error fetching continents: {e}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500
    finally:
        if conn:
            conn.close()

@locations_bp.route('/countries', methods=['GET'])
def get_countries_by_continent():
    """특정 대륙에 속한 국가 목록을 반환합니다."""
    continent_ko = request.args.get('continent')
    if not continent_ko:
        return jsonify({"error": "'continent' 쿼리 파라미터가 필요합니다."}), 400

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT country, country_ko, location_id 
                FROM locations 
                WHERE continent_ko = %s AND location_type = 'country' 
                ORDER BY country_ko
            """, (continent_ko,))
            countries = cursor.fetchall()
        return jsonify(countries)
    except Exception as e:
        print(f"Error fetching countries for continent {continent_ko}: {e}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500
    finally:
        if conn:
            conn.close()

@locations_bp.route('/cities', methods=['GET'])
def get_cities_by_country():
    """특정 국가에 속한 도시 목록을 반환합니다."""
    country_ko = request.args.get('country')
    if not country_ko:
        return jsonify({"error": "'country' 쿼리 파라미터가 필요합니다."}), 400

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT city_ko, location_id 
                FROM locations 
                WHERE country_ko = %s AND location_type = 'city' 
                ORDER BY city_ko
            """, (country_ko,))
            cities = cursor.fetchall()
        return jsonify(cities)
    except Exception as e:
        print(f"Error fetching cities for country {country_ko}: {e}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500
    finally:
        if conn:
            conn.close()

@locations_bp.route('/<int:location_id>', methods=['GET'])
def get_location_details(location_id):
    """특정 위치 ID에 대한 상세 정보를 반환합니다."""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM locations WHERE location_id = %s", (location_id,))
            location = cursor.fetchone()
            if not location:
                return jsonify({"error": "해당 위치를 찾을 수 없습니다."}), 404

            cursor.execute("SELECT * FROM budgets WHERE location_id = %s", (location_id,))
            budget = cursor.fetchone()

            cursor.execute("SELECT * FROM cost_breakdowns WHERE location_id = %s", (location_id,))
            cost_breakdowns = cursor.fetchall()

            cursor.execute("SELECT * FROM location_content WHERE location_id = %s", (location_id,))
            location_content = cursor.fetchall()

        response_data = {
            "location": location,
            "budget": budget,
            "cost_breakdowns": cost_breakdowns,
            "location_content": location_content
        }
        return jsonify(response_data)

    except Exception as e:
        print(f"Error fetching location details for {location_id}: {e}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500
    finally:
        if conn:
            conn.close()

@locations_bp.route('/country-map', methods=['GET'])
def get_country_map():
    """DB에서 국가 영문 이름과 location_id의 매핑을 생성하여 반환합니다."""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 데이터베이스에서 중복을 제거하고 국가 이름과 location_id를 가져옵니다.
            # location_type이 'country'인 경우만 필터링합니다.
            cursor.execute("""
                SELECT country, location_id 
                FROM locations 
                WHERE location_type = 'country'
            """)
            # 결과를 딕셔너리 형태로 변환합니다: {"country_name": location_id}
            country_map = {row['country']: row['location_id'] for row in cursor.fetchall()}
        return jsonify(country_map)
    except Exception as e:
        print(f"Error fetching country map: {e}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500
    finally:
        if conn:
            conn.close()