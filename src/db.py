import os
import mysql.connector
from mysql.connector import Error, pooling
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수에서 DB 설정 가져오기
DB_CONFIG = {
    "host": os.getenv("DATABASE_HOST", "localhost"),
    "user": os.getenv("DATABASE_USER", "root"),
    "password": os.getenv("DATABASE_PASSWORD"),
    "database": os.getenv("DATABASE_NAME"),
    "pool_name": "mypool",
    "pool_size": 5,  # 최대 5개의 연결 유지
}

# Connection Pool 생성
try:
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(**DB_CONFIG)
    print("✅ MariaDB Connection Pool 생성 완료")
except Error as e:
    print(f"❌ Connection Pool 생성 실패: {e}")
    connection_pool = None


def get_connection():
    """Connection Pool에서 연결 가져오기"""
    if connection_pool:
        try:
            return connection_pool.get_connection()
        except Error as e:
            print(f"❌ Connection Pool에서 연결 가져오기 실패: {e}")
    return None


def execute_query(query, params=None):
    """
    INSERT, UPDATE, DELETE 실행 후 성공 여부 반환
    :param query: 실행할 SQL 쿼리
    :param params: SQL 쿼리의 파라미터 (tuple or dict)
    :return: 실행 성공 여부 (True/False)
    """
    conn = get_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return True
    except Error as e:
        print(f"❌ 쿼리 실행 오류: {e}")
        return False
    finally:
        cursor.close()
        conn.close()  # 연결 반환


def fetch_query(query, params=None):
    """
    SELECT 쿼리를 실행하고 결과를 반환
    :param query: 실행할 SQL 쿼리
    :param params: SQL 쿼리의 파라미터 (tuple or dict)
    :return: 조회된 데이터 (list of dict)
    """
    conn = get_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"❌ 데이터 조회 오류: {e}")
        return None
    finally:
        cursor.close()
        conn.close()  # 연결 반환


def test_db_connection():
    """DB 연결 및 기본 쿼리 실행 테스트"""
    print("🔍 데이터베이스 연결 테스트 중...")
    conn = get_connection()
    if conn is None:
        print("❌ DB 연결 실패")
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        print("✅ DB 연결 테스트 성공")
        return True
    except Error as e:
        print(f"❌ DB 연결 테스트 실패: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


# 테스트 코드 (파일 실행 시 실행됨)
if __name__ == "__main__":
    # 연결 테스트
    connection = get_connection()
    if connection:
        print("✅ MariaDB 연결 성공")
        connection.close()

    # SELECT 예제
    data = fetch_query("SELECT * FROM drum LIMIT 5;")
    print(data)
