passcheckers_backend/
├── app/
│   ├── __init__.py                  # Flask 앱 생성 초기화 파일
│   ├── matching/                    # 매칭 기능
│   │   ├── __init__.py
│   │   ├── item_service.py
│   ├── models/                  # matching 관련 모델
│   │   ├── __init__.py
│   │   └── item_model.py
│   ├── routes/                      # Flask 라우트 (API 엔드포인트)
│   │   ├── __init__.py
│   │   ├── classify.py               # YOLO 추론 API 라우트
│   │   ├── items.py
│   │   ├── weight_predict.py
│   ├── scraping/                     # 스크래핑 관련 스크립트
│   │   ├── translate_csv.py
│   │   └── TSA 규정.py
│   ├── utils/                        # 유틸 함수 모음
│   │   └── helpers.py
│   ├── weight/                       # 무게 예측 관련 코드
│   │   └── predictor.py
│   └── yolo/                         # YOLO 관련 코드
│       ├── weights/           
│       └── detect.py                 # 추론 로직
├── docs/                             # 프로젝트 문서 및 구조 파일
│   ├── dev_tips.md
│   └── structure.md
├── static/                           # 정적 파일 (결과 이미지, 프론트 정적 자원)
│   └── results/
├── templates/                        # (필요한 경우) HTML 템플릿
├── uploads/                          # 사용자 이미지 임시 저장 (gitignore로 제외)
├── venv/                             # 가상환경 폴더 (venv로 추정)
├── .gitignore
├── config.py                         # 환경설정 파일
├── insertDB.py                       # DB 입력 스크립트
├── LICENSE
├── mysql.py                          # MySQL 연결 및 쿼리 관련 모듈
├── populate_db.py                    # DB 초기 데이터 입력용 스크립트
├── README.md
├── requirements.txt                  # Python 패키지 리스트
└── run.py                            # Flask 앱 실행 진입점
