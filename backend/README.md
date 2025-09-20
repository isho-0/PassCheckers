# PassCheckers Backend API

Flask 기반의 백엔드 API 서버입니다.  
AI 이미지 분석, 사용자 인증, 데이터베이스 관리를 담당합니다.

## 📁 디렉터리 구조

```
backend/
├── models/               # 데이터 모델
│   ├── user.py          # 사용자 모델
│   └── pytorch/         # AI 모델 파일
├── repository/          # 데이터 접근 계층
│   └── user_repo.py     # 사용자 데이터 접근
├── service/             # 비즈니스 로직
│   └── user_service.py  # 사용자 서비스
├── routes/              # API 라우트 (미사용)
├── classification/      # 분류 관련 모듈
├── matching/            # 매칭 관련 모듈
├── sku/                 # SKU 관련 모듈
├── yolo/                # YOLO 관련 모듈
├── app.py               # Flask 앱 메인 파일
├── config.py            # 설정 파일
└── requirements.txt     # Python 의존성
```

## ⚠️ 중요 사항

- `backend_merge_file/` 폴더는 **절대 수정하지 마세요**
- 이 폴더는 다른 환경에서 작업된 코드로, 병합 시 참고용입니다
- 모든 수정 작업은 현재 `backend/` 폴더에서 진행하세요

## 설치 및 실행

### 1. Python 가상환경 생성
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
```bash
cp env.example .env
# .env 파일을 편집하여 실제 값으로 변경
```

### 4. 데이터베이스 설정
- MySQL 설치 및 실행
- 데이터베이스 생성: `passcheckers`
- Redis 설치 및 실행

### 5. 서버 실행
```bash
python app.py
```

서버는 `http://localhost:5000`에서 실행됩니다.

## API 엔드포인트

### 인증 관련
- `POST /api/register` - 회원가입
- `POST /api/login` - 로그인
- `POST /api/refresh` - Access Token 재발급
- `POST /api/logout` - 로그아웃

### 사용자 관련
- `GET /api/profile` - 사용자 프로필 조회
- `GET /api/protected` - 인증 테스트

### 시스템
- `GET /api/health` - 서버 상태 확인

### 아이템/이미지 관련
- `GET /api/items/image/<image_id>` - ID에 해당하는 원본 이미지를 반환합니다.
- `GET /api/items/all` - DB에 저장된 모든 품목 정보를 가져옵니다.
- `GET /api/items/autocomplete` - 품목 검색 시 자동완성 목록을 제공합니다.
- `POST /api/items/match` - 텍스트와 가장 유사한 품목을 찾습니다.
- `POST /api/items/add` - 이미지에 새로운 품목 정보를 추가합니다.
- `POST /api/items/delete` - 이미지에서 품목 정보를 삭제합니다.
- `GET /api/items/results/<image_id>` - 특정 이미지의 모든 품목 분석 결과를 가져옵니다.

### 이미지 분류
- `POST /classify` - 이미지를 업로드하여 품목을 분류합니다.

### 분석 결과 관련
- `POST /api/analysis/save` - 이미지 분석 결과를 DB에 저장합니다.
- `GET /api/analysis/history/<user_id>` - 특정 사용자의 모든 분석 기록을 가져옵니다.
- `GET /api/analysis/detail/<analysis_id>` - 특정 분석 기록의 상세 정보를 가져옵니다.

## 환경 변수

- `SECRET_KEY`: Flask 시크릿 키
- `JWT_SECRET_KEY`: JWT 시크릿 키
- `REDIS_URL`: Redis 연결 URL
- `DATABASE_URL`: MySQL 연결 URL

## 개발 환경

- Python 3.10+
- Flask 3.0.0
- MySQL 8.0.35
- Redis 
