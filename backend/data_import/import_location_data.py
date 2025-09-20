
import pandas as pd
import pymysql
import os
import sys
from urllib.parse import urlparse

# 상위 디렉토리의 config 모듈 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

def get_db_connection():
    """데이터베이스 연결을 생성합니다."""
    url = os.environ.get('DATABASE_URL')
    if url is None:
        url = Config.SQLALCHEMY_DATABASE_URI

    if 'mysql+pymysql://' in url:
        url = url.replace('mysql+pymysql://', 'mysql://')

    parsed = urlparse(url)
    return pymysql.connect(
        host=parsed.hostname,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path.lstrip('/'),
        port=parsed.port or 3306,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def import_locations(cursor, file_path):
    """locations.csv 파일을 locations 테이블에 삽입합니다."""
    df = pd.read_csv(file_path)
    print(f"Importing {len(df)} rows into 'locations' table...")
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO locations (location_id, continent, continent_ko, country, country_ko, city, city_ko, location_type, geonameid)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['location_id'], row['continent'], row['continent_ko'], row['country'], row['country_ko'],
                row['city'], row['city_ko'], row['location_type'], row['geonameid']
            ))
        except pymysql.err.IntegrityError as e:
            print(f"Skipping duplicate entry for location_id {row['location_id']}: {e}")
        except Exception as e:
            print(f"An error occurred for location_id {row['location_id']}: {e}")
    print("'locations' table import complete.")

def import_budgets(cursor, file_path):
    """budgets.csv 파일을 budgets 테이블에 삽입합니다."""
    df = pd.read_csv(file_path)
    print(f"Importing {len(df)} rows into 'budgets' table...")
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO budgets (location_id, budget_daily, budget_weekly, budget_monthly, midrange_daily, midrange_weekly, midrange_monthly, luxury_daily, luxury_weekly, luxury_monthly)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['location_id'], row['budget_daily'], row['budget_weekly'], row['budget_monthly'],
                row['midrange_daily'], row['midrange_weekly'], row['midrange_monthly'],
                row['luxury_daily'], row['luxury_weekly'], row['luxury_monthly']
            ))
        except pymysql.err.IntegrityError as e:
            print(f"Skipping duplicate or foreign key error for location_id {row['location_id']}: {e}")
        except Exception as e:
            print(f"An error occurred for location_id {row['location_id']}: {e}")
    print("'budgets' table import complete.")

def import_cost_breakdowns(cursor, file_path):
    """cost_breakdowns.csv 파일을 cost_breakdowns 테이블에 삽입합니다."""
    df = pd.read_csv(file_path)
    print(f"Importing {len(df)} rows into 'cost_breakdowns' table...")
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO cost_breakdowns (location_id, table_title, table_title_ko, category, category_ko, budget, mid_range, luxury)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['location_id'], row['table_title'], row['table_title_ko'], row['category'],
                row['category_ko'], row['budget'], row['mid_range'], row['luxury']
            ))
        except pymysql.err.IntegrityError as e:
            print(f"Skipping duplicate or foreign key error for location_id {row['location_id']}: {e}")
        except Exception as e:
            print(f"An error occurred for location_id {row['location_id']}: {e}")
    print("'cost_breakdowns' table import complete.")

def import_location_content(cursor, file_path):
    """location_content.csv 파일을 location_content 테이블에 삽입합니다."""
    chunk_size = 1000
    print(f"Importing rows from '{os.path.basename(file_path)}' into 'location_content' table in chunks of {chunk_size}...")
    
    total_rows = 0
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        chunk = chunk.where(pd.notnull(chunk), None) # Replace NaN with None for SQL NULL
        
        rows_in_chunk = 0
        for _, row in chunk.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO location_content (location_id, title_ko, content_ko)
                    VALUES (%s, %s, %s)
                """, (
                    row['location_id'], row['title_ko'], row['content_ko']
                ))
                rows_in_chunk += 1
            except pymysql.err.IntegrityError as e:
                print(f"Skipping duplicate or foreign key error for location_id {row['location_id']}: {e}")
            except Exception as e:
                print(f"An error occurred for location_id {row['location_id']}: {e}")
        
        total_rows += rows_in_chunk
        print(f"  ... {total_rows} rows imported so far.")

    print(f"'location_content' table import complete. Total rows imported: {total_rows}")


def main():
    """메인 함수"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # CSV 파일 경로 (프로젝트 루트 기준)
        base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
        locations_csv = os.path.join(base_path, '1_locations.csv')
        budgets_csv = os.path.join(base_path, '2_budgets.csv')
        cost_breakdowns_csv = os.path.join(base_path, '3_cost_breakdowns.csv')
        location_content_csv = os.path.join(base_path, '4_location_content.csv')

        # Foreign Key 제약 조건 때문에 locations 부터 임포트
        import_locations(cursor, locations_csv)
        conn.commit()

        import_budgets(cursor, budgets_csv)
        conn.commit()

        import_cost_breakdowns(cursor, cost_breakdowns_csv)
        conn.commit()
        
        import_location_content(cursor, location_content_csv)
        conn.commit()

        print("\nAll CSV files have been imported successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()
