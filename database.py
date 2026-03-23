import sqlite3
import os
from datetime import datetime

DB_NAME = "tvguide.db"

def setup_database():
    """데이터베이스 테이블 생성. 로그 테이블 추가."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 편성표 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tv_guide (
            date TEXT,
            category TEXT,
            channel TEXT,
            time TEXT,
            title TEXT
        )
    """)
    
    # 작업 로그 테이블 (스케줄링 상태 기록용)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_logs (
            job_name TEXT,
            target_date TEXT,
            status TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def log_job_status(job_name, target_date, status, message):
    """작업 로그 기록."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO job_logs (job_name, target_date, status, message) VALUES (?, ?, ?, ?)",
                   (job_name, target_date, status, message))
    conn.commit()
    conn.close()

def get_latest_failed_job():
    """최근 실패한 크롤링 작업 조회 (알림용)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # 최근 24시간 이내의 실패 로그 중 가장 최근 것 조회
    cursor.execute("""
        SELECT target_date, message, timestamp 
        FROM job_logs 
        WHERE status = 'FAILED' 
        ORDER BY timestamp DESC 
        LIMIT 1
    """)
    result = cursor.fetchone()
    conn.close()
    return result

def delete_existing_data(date, category):
    """지정된 일자와 카테고리에 해당하는 데이터 삭제."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        if category == 'all':
            cursor.execute("DELETE FROM tv_guide WHERE date = ?", (date,))
        else:
            cursor.execute("DELETE FROM tv_guide WHERE date = ? AND category = ?", (date, category))
        conn.commit()
    except Exception as e:
        print(f"DB DELETE Error: {e}")
    finally:
        conn.close()

def save_tv_guide(data_list):
    """데이터 저장."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.executemany(
            "INSERT INTO tv_guide (date, category, channel, time, title) VALUES (?, ?, ?, ?, ?)", 
            data_list
        )
        conn.commit()
    except Exception as e:
        print(f"DB INSERT Error: {e}")
    finally:
        conn.close()

def get_channels():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT channel FROM tv_guide ORDER BY channel ASC")
    channels = [row[0] for row in cursor.fetchall()]
    conn.close()
    return channels

def get_filtered_guide(date=None, channel=None, category=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = "SELECT date, category, channel, time, title FROM tv_guide WHERE 1=1"
    params = []
    if date:
        query += " AND date = ?"
        params.append(date)
    if channel:
        query += " AND channel = ?"
        params.append(channel)
    if category:
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY time ASC, channel ASC"
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results

def get_now_playing(date, current_time):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT channel FROM tv_guide WHERE date = ?", (date,))
    channels = [row[0] for row in cursor.fetchall()]
    now_playing = []
    for channel in channels:
        cursor.execute("""
            SELECT channel, time, title 
            FROM tv_guide 
            WHERE date = ? AND channel = ? AND time <= ?
            ORDER BY time DESC 
            LIMIT 1
        """, (date, channel, current_time))
        result = cursor.fetchone()
        if result:
            now_playing.append(result)
    conn.close()
    return now_playing
