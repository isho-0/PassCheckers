from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import redis
import pymysql
import os
from datetime import timedelta
from config import Config
from models.user import User
from urllib.parse import urlparse
from functools import wraps
from repository.user_repo import UserRepository
from service.user_service import UserService, UserExistsException, InvalidCredentialsException
from routes.classify import classify_bp
from routes.items import items_bp
from routes.analysis import analysis_bp
from routes.locations import locations_bp

app = Flask(__name__)
app.config.from_object(Config)

# JWT 설정
jwt = JWTManager(app)

# CORS 설정
CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)

# Blueprint 등록
app.register_blueprint(classify_bp)
app.register_blueprint(items_bp)
app.register_blueprint(analysis_bp)
app.register_blueprint(locations_bp)

# Redis 연결
redis_client = redis.from_url(Config.REDIS_URL)

# MySQL 연결
def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url is None:
        raise Exception("DATABASE_URL 환경변수가 설정되지 않았습니다.")

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

# 데이터베이스 초기화
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # users 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            name VARCHAR(100) NOT NULL,
            nickname VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    
    # images 테이블 생성 (이미지 저장용)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(100) NOT NULL,
            image_data LONGBLOB NOT NULL,
            width INT NOT NULL,
            height INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    
    # items 테이블 생성 (물품 정보용)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            item_name VARCHAR(255) NOT NULL UNIQUE,
            item_name_EN VARCHAR(255),
            carry_on_allowed VARCHAR(50),
            checked_baggage_allowed VARCHAR(50),
            notes TEXT,
            notes_EN TEXT,
            source VARCHAR(50) DEFAULT 'manual'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    
    # 기존 테이블에 notes_EN 컬럼이 없으면 추가
    try:
        cursor.execute("ALTER TABLE items ADD COLUMN notes_EN TEXT")
        print("Added notes_EN column to items table")
    except Exception as e:
        if "Duplicate column name" in str(e):
            print("notes_EN column already exists")
        else:
            print(f"Error adding notes_EN column: {e}")
    
    # 기존 테이블에 source 컬럼이 없으면 추가
    try:
        cursor.execute("ALTER TABLE items ADD COLUMN source VARCHAR(50) DEFAULT 'manual'")
        print("Added source column to items table")
    except Exception as e:
        if "Duplicate column name" in str(e):
            print("source column already exists")
        else:
            print(f"Error adding source column: {e}")
    
    # detected_items 테이블 생성 (탐지된 물품용)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detected_items (
            item_id INT AUTO_INCREMENT PRIMARY KEY,
            image_id INT NOT NULL,
            item_name_EN VARCHAR(255),
            item_name VARCHAR(255) NOT NULL,
            bbox_x_min FLOAT NOT NULL,
            bbox_y_min FLOAT NOT NULL,
            bbox_x_max FLOAT NOT NULL,
            bbox_y_max FLOAT NOT NULL,
            packing_info VARCHAR(50) DEFAULT 'none',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    
    conn.commit()
    cursor.close()
    conn.close()

def api_handler(required_fields=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                data = request.get_json(force=True, silent=True) or {}
                if required_fields:
                    missing = [f for f in required_fields if not data.get(f)]
                    if missing:
                        return jsonify({'error': f"필수 입력값 누락: {', '.join(missing)}"}), 400
                return func(data, *args, **kwargs)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        return wrapper
    return decorator

# API 라우트

@app.route('/api/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return jsonify({'status': 'healthy', 'message': 'Server is running'})

@app.route('/api/register', methods=['POST'])
@api_handler(required_fields=['email', 'password', 'name', 'nickname'])
def register(data):
    conn = get_db_connection()
    user_repo = UserRepository(conn)
    user_service = UserService(user_repo)
    try:
        user = user_service.register(
            data['email'], data['password'], data['name'], data['nickname']
        )
        conn.close()
        return jsonify({
            'message': '회원가입이 완료되었습니다',
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'nickname': user['nickname'],
                'created_at': user['created_at']
            }
        }), 201
    except UserExistsException as e:
        conn.close()
        return jsonify({'error': str(e)}), 409
    except Exception as e:
        conn.close()
        return jsonify({'error': '서버 오류가 발생했습니다'}), 500

@app.route('/api/login', methods=['POST'])
@api_handler(required_fields=['email', 'password'])
def login(data):
    conn = get_db_connection()
    user_repo = UserRepository(conn)
    user_service = UserService(user_repo)
    try:
        user = user_service.login(data['email'], data['password'])
        conn.close()
        access_token = create_access_token(identity=user['id'])
        refresh_token = create_refresh_token(identity=user['id'])
        redis_client.setex(
            f"refresh_token:{user['id']}",
            86400,
            refresh_token
        )
        return jsonify({
            'message': '로그인 성공',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'nickname': user['nickname'],
                'created_at': user['created_at']
            }
        }), 200
    except InvalidCredentialsException as e:
        conn.close()
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        conn.close()
        return jsonify({'error': '서버 오류가 발생했습니다'}), 500

@app.route('/api/refresh', methods=['POST'])
@jwt_required(refresh=True)
@api_handler()
def refresh(data=None):
    current_user_id = get_jwt_identity()
    stored_refresh_token = redis_client.get(f"refresh_token:{current_user_id}")
    if not stored_refresh_token:
        return jsonify({'error': '유효하지 않은 Refresh Token입니다'}), 401
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify({'access_token': new_access_token}), 200

@app.route('/api/logout', methods=['POST'])
@jwt_required()
@api_handler()
def logout(data=None):
    current_user_id = get_jwt_identity()
    redis_client.delete(f"refresh_token:{current_user_id}")
    return jsonify({'message': '로그아웃되었습니다'}), 200

@app.route('/api/profile', methods=['GET'])
@jwt_required()
@api_handler()
def get_profile(data=None):
    current_user_id = get_jwt_identity()
    conn = get_db_connection()
    user_model = User(conn)
    user = user_model.get_user_by_id(current_user_id)
    conn.close()
    if not user:
        return jsonify({'error': '사용자를 찾을 수 없습니다'}), 404
    return jsonify({'user': user}), 200

@app.route('/api/protected', methods=['GET'])
@jwt_required()
@api_handler()
def protected(data=None):
    current_user_id = get_jwt_identity()
    return jsonify({
        'message': '인증된 사용자만 접근 가능합니다',
        'user_id': current_user_id
    }), 200

if __name__ == '__main__':
    # 데이터베이스 초기화
    init_db()
    
    # 개발 서버 실행
    app.run(debug=True, host='0.0.0.0', port=5001) 