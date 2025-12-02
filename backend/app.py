from flask import Flask, request, jsonify, send_file
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from dotenv import load_dotenv
import redis
import pymysql
import os
import io
from datetime import timedelta
from config import Config

load_dotenv()
from models.user import User
from urllib.parse import urlparse
from functools import wraps
from repository.user_repo import UserRepository
from service.user_service import UserService, UserExistsException, InvalidCredentialsException
from routes.classify import classify_bp
from routes.items import items_bp
from routes.analysis import analysis_bp
from routes.locations import locations_bp
from routes.weight import weight_bp
from routes.category import category_bp
from routes.packing import packing_bp
from routes.share import share_bp
from routes.recommend import recommend_bp
from routes.flights import flights_bp
from routes.matching import matching_bp
from routes.community import community_bp
from routes.user import user_bp

app = Flask(__name__)
app.config.from_object(Config)

# JWT 설정
jwt = JWTManager(app)

# CORS 설정
CORS(app, 
     origins=Config.CORS_ORIGINS, 
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     expose_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# 블루프린트 등록
app.register_blueprint(classify_bp)
app.register_blueprint(items_bp)
app.register_blueprint(analysis_bp)
app.register_blueprint(locations_bp)
app.register_blueprint(weight_bp)
app.register_blueprint(category_bp)
app.register_blueprint(packing_bp)
app.register_blueprint(share_bp)
app.register_blueprint(recommend_bp, url_prefix='/api')
app.register_blueprint(flights_bp, url_prefix='/api')
app.register_blueprint(matching_bp, url_prefix='/api/matching')
app.register_blueprint(community_bp)
app.register_blueprint(user_bp)

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
        cursorclass=pymysql.cursors.DictCursor,
        init_command="SET time_zone = '+09:00'"
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

    # 스키마 마이그레이션: users 테이블에 profile_image 컬럼이 없는 경우 추가
    db_name = conn.db.decode() if isinstance(conn.db, bytes) else conn.db
    cursor.execute("""        SELECT COUNT(*) as cnt
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s
        AND TABLE_NAME = 'users'
        AND COLUMN_NAME = 'profile_image'
    """, (db_name,))
    if cursor.fetchone()['cnt'] == 0:
        cursor.execute("ALTER TABLE users ADD COLUMN profile_image LONGBLOB NULL")
        print("[DB MIGRATION] 'profile_image' column added to 'users' table.")

    
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

    # 스키마 마이그레이션: items 테이블에 category 컬럼이 없는 경우 추가
    db_name = conn.db.decode() if isinstance(conn.db, bytes) else conn.db
    cursor.execute("""
        SELECT COUNT(*) as cnt
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s
        AND TABLE_NAME = 'items'
        AND COLUMN_NAME = 'category'
    """, (db_name,))
    if cursor.fetchone()['cnt'] == 0:
        cursor.execute("ALTER TABLE items ADD COLUMN category VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL")
        print("[DB MIGRATION] 'category' column added to 'items' table.")
    
    # locations 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            location_id INT AUTO_INCREMENT PRIMARY KEY,
            continent VARCHAR(50),
            continent_ko VARCHAR(50),
            country VARCHAR(100),
            country_ko VARCHAR(100),
            city VARCHAR(100),
            city_ko VARCHAR(100),
            location_type VARCHAR(10) NOT NULL,
            geonameid INT,
            UNIQUE KEY uk_geonameid_type (geonameid, location_type) 
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # budgets 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            location_id INT PRIMARY KEY,
            budget_daily INT,
            budget_weekly INT,
            budget_monthly INT,
            midrange_daily INT,
            midrange_weekly INT,
            midrange_monthly INT,
            luxury_daily INT,
            luxury_weekly INT,
            luxury_monthly INT,
            FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # cost_breakdowns 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cost_breakdowns (
            breakdown_id INT AUTO_INCREMENT PRIMARY KEY,
            location_id INT,
            table_title VARCHAR(255),
            table_title_ko VARCHAR(255),
            category VARCHAR(100),
            category_ko VARCHAR(100),
            budget VARCHAR(50),
            mid_range VARCHAR(50),
            luxury VARCHAR(50),
            FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # location_content 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS location_content (
            content_id INT AUTO_INCREMENT PRIMARY KEY,
            location_id INT,
            title_ko VARCHAR(255),
            content_ko TEXT,
            FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # analysis_results 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL,
            image_id INT NOT NULL,
            image_url TEXT,
            image_width INT,
            image_height INT,
            total_items INT NOT NULL,
            analysis_date DATETIME NOT NULL,
            destination VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # analysis_items 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            analysis_id INT NOT NULL,
            item_name_ko VARCHAR(255) NOT NULL,
            item_name_en VARCHAR(255),
            confidence DECIMAL(5,4),
            carry_on_allowed VARCHAR(100),
            checked_baggage_allowed VARCHAR(100),
            notes TEXT,
            notes_EN TEXT,
            source VARCHAR(50),
            bbox_x_min DECIMAL(10,8),
            bbox_y_min DECIMAL(10,8),
            bbox_x_max DECIMAL(10,8),
            bbox_y_max DECIMAL(10,8),
            predicted_weight_value DECIMAL(10,2),
            predicted_weight_unit VARCHAR(10),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (analysis_id) REFERENCES analysis_results(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # 스키마 마이그레이션: analysis_results 테이블에 share_code 컬럼이 없는 경우 추가
    cursor.execute("""
        SELECT COUNT(*) as cnt
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s
        AND TABLE_NAME = 'analysis_results'
        AND COLUMN_NAME = 'share_code'
    """, (db_name,))
    if cursor.fetchone()['cnt'] == 0:
        cursor.execute("ALTER TABLE analysis_results ADD COLUMN share_code VARCHAR(10) UNIQUE AFTER destination")
        print("[DB MIGRATION] 'share_code' 컬럼이 'analysis_results' 테이블에 추가되었습니다.")

    # ===== 커뮤니티 테이블 생성 =====
    
    # posts 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            summary VARCHAR(500),
            location VARCHAR(255),
            image_id INT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            likes_count INT DEFAULT 0,
            comments_count INT DEFAULT 0,
            views_count INT DEFAULT 0,
            is_deleted BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE SET NULL,
            INDEX idx_created_at (created_at),
            INDEX idx_location (location),
            INDEX idx_user_id (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    
    # tags 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_name (name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    
    # post_tags 연결 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS post_tags (
            id INT AUTO_INCREMENT PRIMARY KEY,
            post_id INT NOT NULL,
            tag_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
            UNIQUE KEY unique_post_tag (post_id, tag_id),
            INDEX idx_post_id (post_id),
            INDEX idx_tag_id (tag_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    
    # comments 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            post_id INT NOT NULL,
            user_id INT NOT NULL,
            content TEXT NOT NULL,
            parent_comment_id INT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            is_deleted BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (parent_comment_id) REFERENCES comments(id) ON DELETE CASCADE,
            INDEX idx_post_id (post_id),
            INDEX idx_user_id (user_id),
            INDEX idx_parent_comment_id (parent_comment_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    
    # post_likes 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS post_likes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            post_id INT NOT NULL,
            user_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE KEY unique_post_like (post_id, user_id),
            INDEX idx_post_id (post_id),
            INDEX idx_user_id (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    
    # post_bookmarks 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS post_bookmarks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            post_id INT NOT NULL,
            user_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE KEY unique_post_bookmark (post_id, user_id),
            INDEX idx_post_id (post_id),
            INDEX idx_user_id (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # 스키마 마이그레이션: items 테이블에 category 컬럼이 없는 경우 추가
    db_name = conn.db.decode() if isinstance(conn.db, bytes) else conn.db
    cursor.execute("""
        SELECT COUNT(*) as cnt
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s
        AND TABLE_NAME = 'items'
        AND COLUMN_NAME = 'category'
    """, (db_name,))
    if cursor.fetchone()['cnt'] == 0:
        cursor.execute("ALTER TABLE items ADD COLUMN category VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL")
        print("[DB MIGRATION] 'category' column added to 'items' table.")
    # share_connections 테이블 생성 (공유 기능용)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS share_connections (
            id INT AUTO_INCREMENT PRIMARY KEY,
            host_analysis_id INT NOT NULL,
            partner_analysis_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (host_analysis_id) REFERENCES analysis_results(id) ON DELETE CASCADE,
            FOREIGN KEY (partner_analysis_id) REFERENCES analysis_results(id) ON DELETE CASCADE,
            UNIQUE KEY uk_connection (host_analysis_id, partner_analysis_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    print("share_connections table checked/created.")

    # share_comments 테이블 생성 (공유 댓글 기능용)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS share_comments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            analysis_id INT NOT NULL,
            user_id INT NOT NULL,
            content VARCHAR(1000) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (analysis_id) REFERENCES analysis_results(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    print("share_comments table checked/created.")
    
    # 스키마 마이그레이션: posts 테이블에 image_id 컬럼이 없는 경우 추가
    cursor.execute("""
        SELECT COUNT(*) as cnt
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s
        AND TABLE_NAME = 'posts'
        AND COLUMN_NAME = 'image_id'
    """, (db_name,))
    if cursor.fetchone()['cnt'] == 0:
        cursor.execute("""
            ALTER TABLE posts 
            ADD COLUMN image_id INT DEFAULT NULL,
            ADD CONSTRAINT fk_posts_image FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE SET NULL
        """)
        print("[DB MIGRATION] 'image_id' column added to 'posts' table.")
    
    # 기존 image_url 컬럼이 있으면 제거 (image_id로 전환)
    cursor.execute("""
        SELECT COUNT(*) as cnt
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s
        AND TABLE_NAME = 'posts'
        AND COLUMN_NAME = 'image_url'
    """, (db_name,))
    if cursor.fetchone()['cnt'] > 0:
        cursor.execute("ALTER TABLE posts DROP COLUMN image_url")
        print("[DB MIGRATION] 'image_url' column removed from 'posts' table.")
    
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

@app.route('/api/profile/image', methods=['GET'])
@jwt_required()
def get_my_profile_image():
    """현재 로그인한 사용자의 프로필 이미지 조회"""
    current_user_id = get_jwt_identity()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT profile_image FROM users WHERE id = %s", (current_user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not result:
            return jsonify({'error': '사용자를 찾을 수 없습니다'}), 404
        
        profile_image = result.get('profile_image')
        
        # 프로필 이미지가 없으면 기본 이미지 반환
        if not profile_image:
            # 기본 프로필 이미지 경로
            default_image_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'frontend', 'public', 'images', 'default_profile.png'
            )
            if os.path.exists(default_image_path):
                return send_file(default_image_path, mimetype='image/png')
            else:
                return jsonify({'error': '프로필 이미지가 없습니다'}), 404
        
        # BLOB 데이터를 이미지로 반환
        return send_file(
            io.BytesIO(profile_image),
            mimetype='image/png',
            as_attachment=False
        )
    except Exception as e:
        cursor.close()
        conn.close()
        print(f"프로필 이미지 조회 오류: {e}")
        return jsonify({'error': '프로필 이미지를 불러오는 중 오류가 발생했습니다'}), 500

@app.route('/api/users/<int:user_id>/profile-image', methods=['GET'])
def get_user_profile_image(user_id):
    """특정 사용자의 프로필 이미지 조회 (공개)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT profile_image FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not result:
            return jsonify({'error': '사용자를 찾을 수 없습니다'}), 404
        
        profile_image = result.get('profile_image')
        
        # 프로필 이미지가 없으면 기본 이미지 반환
        if not profile_image:
            default_image_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'frontend', 'public', 'images', 'default_profile.png'
            )
            if os.path.exists(default_image_path):
                return send_file(default_image_path, mimetype='image/png')
            else:
                return jsonify({'error': '프로필 이미지가 없습니다'}), 404
        
        # BLOB 데이터를 이미지로 반환
        return send_file(
            io.BytesIO(profile_image),
            mimetype='image/png',
            as_attachment=False
        )
    except Exception as e:
        cursor.close()
        conn.close()
        print(f"프로필 이미지 조회 오류: {e}")
        return jsonify({'error': '프로필 이미지를 불러오는 중 오류가 발생했습니다'}), 500

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