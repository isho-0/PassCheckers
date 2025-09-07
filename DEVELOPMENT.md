# 🛠️ PassCheckers 개발 가이드

## 📋 프로젝트 구조 개선 완료 사항

### ✅ 완료된 작업

1. **프론트엔드 분리**
   - 루트 디렉터리의 모든 프론트엔드 코드를 `frontend/` 폴더로 이동
   - Nuxt 3, Vue 3, TypeScript 관련 파일들 정리

2. **로그 파일 정리**
   - 모든 로그 파일을 `logs/` 폴더로 통합
   - `backend.log`, `frontend.log` 파일 정리

3. **문서화 개선**
   - 프로젝트 루트에 통합된 README.md 생성
   - 백엔드 README.md 업데이트
   - 개발 가이드 문서 생성

4. **디렉터리 구조 최적화**
   - 명확한 폴더 분리로 개발 효율성 향상
   - 백엔드와 프론트엔드의 명확한 구분

## 🚧 향후 작업 예정

### 백엔드 코드 통합 (수동 작업 필요)
- `backend_merge_file/`의 기능을 `backend/`로 병합
- 중복 코드 제거 및 통합
- AI 모델 관련 코드 통합

### 추가 개선 사항
- 환경별 설정 파일 분리 (dev, staging, production)
- Docker 컨테이너화
- CI/CD 파이프라인 구축
- 테스트 코드 작성

## 📁 현재 프로젝트 구조

```
PassCheckers/
├── frontend/                  # ✅ 프론트엔드 (Nuxt 3)
│   ├── pages/                # Vue 페이지
│   ├── components/           # Vue 컴포넌트
│   ├── composables/          # Vue 컴포저블
│   ├── middleware/           # Nuxt 미들웨어
│   ├── layouts/              # 레이아웃
│   ├── assets/               # 정적 자산
│   ├── public/               # 공개 리소스
│   ├── server/               # SSR 코드
│   ├── app.vue               # 메인 앱
│   ├── nuxt.config.ts        # Nuxt 설정
│   ├── package.json          # 의존성
│   └── tsconfig.json         # TS 설정
│
├── backend/                  # ✅ 기존 백엔드 (Flask)
│   ├── models/               # 데이터 모델
│   ├── repository/           # DB 접근
│   ├── service/              # 비즈니스 로직
│   ├── routes/               # API 라우트
│   ├── classification/       # 분류 모듈
│   ├── matching/             # 매칭 모듈
│   ├── sku/                  # SKU 모듈
│   ├── yolo/                 # YOLO 모듈
│   ├── app.py                # Flask 앱
│   ├── config.py             # 설정
│   ├── requirements.txt      # 의존성
│   └── venv/                 # 가상환경
│
├── backend_merge_file/       # ⚠️ 병합 예정 (수정 금지)
│   ├── yolo/                 # YOLO 객체 탐지
│   ├── sku/                  # SKU 분류
│   ├── routes/               # API 라우트
│   ├── services/             # 외부 서비스
│   ├── models/               # 데이터 모델
│   ├── matching/             # 매칭 로직
│   └── db/                   # 데이터베이스
│
├── logs/                     # ✅ 로그 파일
│   ├── backend.log           # 백엔드 로그
│   └── frontend.log          # 프론트엔드 로그
│
├── README.md                 # ✅ 프로젝트 문서
├── DEVELOPMENT.md            # ✅ 개발 가이드
└── .gitignore               # Git 무시 파일
```

## 🔧 개발 환경 설정

### 프론트엔드 개발
```bash
cd frontend
npm install
npm run dev -- --host
```

### 백엔드 개발
```bash
cd backend
source venv/bin/activate
python3 app.py
```

## ⚠️ 주의사항

1. **`backend_merge_file/` 폴더는 절대 수정하지 마세요**
   - 다른 환경에서 작업된 코드
   - 병합 시 참고용으로만 사용
   - 모든 수정은 `backend/` 폴더에서 진행

2. **프론트엔드 코드**
   - 모든 프론트엔드 관련 작업은 `frontend/` 폴더에서 진행
   - 루트 디렉터리에는 프론트엔드 코드가 없음

3. **로그 파일**
   - 모든 로그는 `logs/` 폴더에 저장
   - 로그 파일은 Git에 커밋하지 않음

## 📝 다음 단계

1. 백엔드 코드 통합 작업 진행
2. 환경별 설정 파일 분리
3. Docker 컨테이너화
4. 테스트 코드 작성
5. CI/CD 파이프라인 구축
