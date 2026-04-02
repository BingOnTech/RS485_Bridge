import sqlite3
import json
from datetime import datetime

class DBManager:
    def __init__(self, config_file='config.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.config['db_name'], check_same_thread=False)
            self.cursor = self.conn.cursor()
            # 테이블 생성 (없으면)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS drum_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    drum_index INTEGER,
                    temperature REAL,
                    level TEXT,
                    valve_in INTEGER,
                    valve_out INTEGER
                )
            ''')
            self.conn.commit()
            print("✅ [Startup] DB 연결 및 테이블 확인 완료")
            return True
        except Exception as e:
            print(f"❌ [Startup] DB 연결 실패: {e}")
            return False

    def insert_log(self, drum_data_list):
        # drum_data_list: [{drum_idx: 1, temp: 25.5, ...}, ...]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            for data in drum_data_list:
                self.cursor.execute('''
                    INSERT INTO drum_logs (timestamp, drum_index, temperature, level, valve_in, valve_out)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (timestamp, data['id'], data['temp'], data['level'], data['in'], data['out']))
            self.conn.commit()
        except Exception as e:
            print(f"⚠️ DB 저장 실패: {e}")

    def close(self):
        if self.conn:
            self.conn.close()