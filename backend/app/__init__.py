from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config

# db 객체를 전역적으로 생성
db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # db 객체를 Flask 앱과 연결
    db.init_app(app)

    # CORS 및 JWT 초기화
    CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)
    jwt = JWTManager(app)
    
    # --- 서비스 초기화 ---
    # 블루프린트를 등록하기 전에, 의존성이 있는 서비스를 먼저 초기화합니다.
    from .matching.item_service import item_service
    item_service.init_app(app)

    
    # --- 블루프린트 등록 ---
    from .routes.classify import classify_bp
    from .routes.items import items_bp
    from .routes.auth import auth_bp  # auth 블루프린트 import

    app.register_blueprint(classify_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(auth_bp)  # auth 블루프린트 등록

    return app