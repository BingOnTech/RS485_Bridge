import mysql.connector
import csv
import os
from dotenv import load_dotenv
from pathlib import Path

# .env 파일 로드
load_dotenv()

# 환경 변수 가져오기
DB_CONFIG = {
    "host": os.getenv("DATABASE_HOST"),
    "user": os.getenv("DATABASE_USER"),
    "password": os.getenv("DATABASE_PASSWORD"),
    "database": os.getenv("DATABASE_NAME"),
}

# 조회할 날짜 범위 설정
START_DATE = "2025-03-17"
END_DATE = "2025-03-20"

# CSV 저장 폴더 설정
DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)  # data 폴더 생성 (없으면 자동 생성)

# 데이터 조회 함수 (각 드럼별 데이터)
def fetch_data(drum_num):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        query = """
            SELECT num, temp, TIMESTAMP 
            FROM drum 
            WHERE num = %s
            AND DATE(TIMESTAMP) BETWEEN %s AND %s
            ORDER BY TIMESTAMP;
        """
        cursor.execute(query, (drum_num, START_DATE, END_DATE))
        results = cursor.fetchall()
        return results

    except mysql.connector.Error as err:
        print(f"❌ Database error: {err}")
        return []

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# CSV 저장 함수 (각 드럼별)
def save_to_csv(drum_num, data):
    if not data:
        print(f"⚠️ No data found for drum {drum_num}")
        return

    file_path = DATA_DIR / f"{drum_num}.csv"
    
    with file_path.open(mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["num", "temp", "timestamp"])  # 헤더 작성
        writer.writerows(data)  # 데이터 작성

    print(f"✅ CSV 저장 완료: {file_path.resolve()}")

# 실행
if __name__ == "__main__":
    for drum_num in range(1, 61):  # 1번부터 60번 드럼까지 순회
        data = fetch_data(drum_num)
        save_to_csv(drum_num, data)
