import os
from dotenv import load_dotenv
load_dotenv() # .env 파일에서 환경 변수를 로드

class Config:
    # 데이터베이스 설정
    # create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}?charset=utf8mb4")
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:5429@localhost/project?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CORS 설정: 프론트엔드 요청을 허용할 주소 목록
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

    # Redis 설정
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

    # (선택) 애플리케이션의 다른 설정들을 추가할 수 있습니다.
    # 예: SECRET_KEY, JWT_SECRET_KEY 등
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-hard-to-guess-string'

    # 제미나이 API 키 삽입(.env 파일 생성하고 해당 이름 변수에 삽입하면 됨)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')