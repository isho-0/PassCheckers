# 수하물 규정 데이터 가져오기

이 폴더는 수하물 규정 데이터를 CSV 파일에서 MySQL 데이터베이스로 가져오는 기능을 제공합니다.

## 파일 구조

```
data_import/
├── import_csv_to_mysql.py    # CSV → MySQL 가져오기 스크립트
├── luggage_regulations.csv   # 수하물 규정 데이터 (자동 생성됨)
└── README.md                 # 이 파일
```

## 사용 방법

### 1. 샘플 데이터로 시작하기

```bash
cd backend/data_import
python3 import_csv_to_mysql.py
```

이 명령어를 실행하면:
- 샘플 수하물 규정 데이터가 `luggage_regulations.csv` 파일로 생성됩니다
- 해당 데이터가 MySQL 데이터베이스에 저장됩니다

### 2. 기존 CSV 파일 사용하기

1. `luggage_regulations.csv` 파일을 이 폴더에 복사합니다
2. CSV 파일의 컬럼 구조는 다음과 같아야 합니다:

```csv
item_name,item_name_EN,carry_on_allowed,checked_baggage_allowed,notes,notes_EN,source
노트북,Laptop,예,예,노트북은 기내 및 위탁 수하물 모두 반입 가능합니다.,Laptops are allowed in both carry-on and checked baggage.,manual
```

3. 스크립트를 실행합니다:
```bash
python3 import_csv_to_mysql.py
```

## CSV 파일 컬럼 설명

| 컬럼명 | 설명 | 예시 |
|--------|------|------|
| `item_name` | 물품 한국어 이름 | 노트북 |
| `item_name_EN` | 물품 영어 이름 | Laptop |
| `carry_on_allowed` | 기내 반입 허용 여부 | 예, 아니요, 예 (특별 지침), 예 (3.4oz/100 ml 이상 또는 동일) |
| `checked_baggage_allowed` | 위탁 수하물 허용 여부 | 예, 아니요, 예 (특별 지침) |
| `notes` | 한국어 설명 | 노트북은 기내 및 위탁 수하물 모두 반입 가능합니다. |
| `notes_EN` | 영어 설명 | Laptops are allowed in both carry-on and checked baggage. |
| `source` | 데이터 출처 | manual, API |

## 주의사항

- 기존 데이터를 삭제하고 새로 시작할지 묻는 메시지가 나타납니다
- 데이터베이스 연결 정보는 `config.py`에서 가져옵니다
- CSV 파일은 UTF-8 BOM 인코딩으로 저장되어야 합니다

## 샘플 데이터

스크립트는 다음과 같은 샘플 데이터를 생성합니다:

- 노트북 (Laptop)
- 액체류 (Liquids)
- 칼 (Knives)
- 담배 (Cigarettes)
- 가방 (General Bag)
- 튜브 (Tube)
- 병 (Bottle)
- 가위 (Scissors)
- 쌈장 (Sauce)
