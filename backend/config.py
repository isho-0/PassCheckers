import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask 설정
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # JWT 설정
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1시간
    JWT_REFRESH_TOKEN_EXPIRES = 86400  # 24시간
    
    # Redis 설정
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # MySQL 설정
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'mysql+pymysql://username:password@localhost:3306/passcheckers'
    
    # CORS 설정
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://passcheckers.kro.kr"
    ] 