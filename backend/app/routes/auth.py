from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from functools import wraps
import redis
from config import Config
from repository.user_repo import UserRepository
from service.user_service import UserService, UserExistsException, InvalidCredentialsException
from app.db.database import get_db_connection

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

# Redis 연결
redis_client = redis.from_url(Config.REDIS_URL)

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

@auth_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Server is running'})

@auth_bp.route('/register', methods=['POST'])
@api_handler(required_fields=['id', 'email', 'password', 'name', 'nickname'])
def register(data):
    conn = get_db_connection()
    user_repo = UserRepository(conn)
    user_service = UserService(user_repo)
    try:
        user = user_service.register(
            data['id'], data['email'], data['password'], data['name'], data['nickname']
        )
        conn.close()
        return jsonify({
            'message': '회원가입이 완료되었습니다',
            'user': user
        }), 201
    except UserExistsException as e:
        conn.close()
        return jsonify({'error': str(e)}), 409
    except Exception as e:
        conn.close()
        return jsonify({'error': '서버 오류가 발생했습니다'}), 500

@auth_bp.route('/login', methods=['POST'])
@api_handler(required_fields=['email', 'password'])
def login(data):
    conn = get_db_connection()
    user_repo = UserRepository(conn)
    user_service = UserService(user_repo)
    try:
        user = user_service.login(data['email'], data['password'])
        conn.close()
        access_token = create_access_token(identity=user['user_id'])
        refresh_token = create_refresh_token(identity=user['user_id'])
        redis_client.setex(
            f"refresh_token:{user['user_id']}",
            86400,
            refresh_token
        )
        return jsonify({
            'message': '로그인 성공',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user
        }), 200
    except InvalidCredentialsException as e:
        conn.close()
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        conn.close()
        return jsonify({'error': '서버 오류가 발생했습니다'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@api_handler()
def refresh(data=None):
    current_user_id = get_jwt_identity()
    stored_refresh_token = redis_client.get(f"refresh_token:{current_user_id}")
    if not stored_refresh_token:
        return jsonify({'error': '유효하지 않은 Refresh Token입니다'}), 401
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify({'access_token': new_access_token}), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
@api_handler()
def logout(data=None):
    current_user_id = get_jwt_identity()
    redis_client.delete(f"refresh_token:{current_user_id}")
    return jsonify({'message': '로그아웃되었습니다'}), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
@api_handler()
def get_profile(data=None):
    current_user_id = get_jwt_identity()
    conn = get_db_connection()
    user_repo = UserRepository(conn)
    user = user_repo.get_by_user_id(current_user_id)
    conn.close()
    if not user:
        return jsonify({'error': '사용자를 찾을 수 없습니다'}), 404
    return jsonify({'user': user}), 200

@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
@api_handler()
def protected(data=None):
    current_user_id = get_jwt_identity()
    return jsonify({
        'message': '인증된 사용자만 접근 가능합니다',
        'user_id': current_user_id
    }), 200