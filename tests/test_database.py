import sqlite3
import pytest
import os
from database import setup_database, save_tv_guide

DB_NAME = "tvguide.db"

@pytest.fixture
def db_setup():
    # 테스트 전에 DB 파일 삭제 (클린 상태)
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    setup_database()
    yield
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

def test_setup_database_creates_table(db_setup):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tv_guide'")
    assert cursor.fetchone() is not None
    conn.close()
