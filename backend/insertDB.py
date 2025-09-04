import pandas as pd
from sqlalchemy import create_engine, exc
import sys

def main():
    user = "root"
    password = "5429"
    host = "localhost"
    database = "project"

    try:
        engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}?charset=utf8mb4")
        
        print("🔄 CSV 파일을 불러오는 중...")
        df = pd.read_csv("tsa_items_trans.csv")

        print("✅ CSV 파일 로드 완료.")
        print("🔍 CSV 컬럼:", df.columns.tolist())

        # 🚫 id 컬럼 제거 (DB에서 자동 증가시키도록 함)
        if "id" in df.columns:
            df = df.drop(columns=["id"])
            print("⚠️ 'id' 컬럼을 제거했습니다. (DB에서 AUTO_INCREMENT 처리)")

        # item_name이 비어있는 행은 삽입하지 않음
        null_item_names = df[
            df['item_name'].isnull() | (df['item_name'].astype(str).str.strip() == '')
        ]

        if not null_item_names.empty:
            print("⚠️ 'item_name'이 널이거나 빈 문자열인 행들이 있습니다. 제외합니다.")
            print(null_item_names)
            df = df.drop(null_item_names.index)

        # DB 저장
        print("🔄 데이터베이스에 데이터를 삽입하는 중...")
        # if_exists="append" → 기존 테이블 구조 유지 + 데이터만 추가
        df.to_sql(name="items", con=engine, if_exists="append", index=False)
        print("✅ 데이터 삽입 완료")

    except FileNotFoundError as e:
        print(f"❌ 파일 오류: {e}")
        sys.exit(1)
    except KeyError as e:
        print(f"❌ 컬럼명 오류: CSV 파일에 {e} 컬럼이 없습니다. CSV 컬럼명을 확인하세요.")
        sys.exit(1)
    except exc.OperationalError as e:
        print(f"❌ DB 연결 오류: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 예기치 않은 오류: {type(e).__name__} - {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
