import sqlite3
import pytest
import os
from database import setup_database, save_tv_guide, get_filtered_guide, DB_NAME

@pytest.fixture
def db_setup():
    # 테스트 전에 DB 파일 삭제 (클린 상태)
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    setup_database()
    yield
    # 테스트 후 파일 삭제
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

def test_setup_database_creates_table(db_setup):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # tv_guide 테이블 존재 확인
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tv_guide'")
    assert cursor.fetchone() is not None
    # job_logs 테이블 존재 확인
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='job_logs'")
    assert cursor.fetchone() is not None
    conn.close()

def test_save_and_retrieve_tv_guide(db_setup):
    test_data = [
        ("2026_03_26", "public", "KBS1", "06:00", "KBS 뉴스광장"),
        ("2026_03_26", "public", "MBC", "07:00", "뉴스투데이")
    ]
    save_tv_guide(test_data)
    
    results = get_filtered_guide(date="2026_03_26")
    assert len(results) == 2
    # 결과 순서는 time ASC, channel ASC (database.py 로직)
    assert results[0][2] == "KBS1"
    assert results[0][3] == "06:00"
    assert results[1][2] == "MBC"
    assert results[1][3] == "07:00"

def test_duplicate_data_replaces_old_one(db_setup):
    """(date, channel, time)이 같은 데이터가 들어오면 기존 것을 덮어쓰는지 확인."""
    # 1. 초기 데이터 삽입
    initial_data = [
        ("2026_03_26", "public", "KBS1", "00:00", "오래된 프로그램")
    ]
    save_tv_guide(initial_data)
    
    # 2. 동일 키(날짜, 채널, 시간)에 다른 카테고리와 제목으로 삽입
    new_data = [
        ("2026_03_26", "public", "KBS1", "00:00", "최신 프로그램 (업데이트됨)")
    ]
    save_tv_guide(new_data)
    
    results = get_filtered_guide(date="2026_03_26", channel="KBS1")
    # 전체 개수는 여전히 1개여야 함
    assert len(results) == 1
    # 제목이 최신 것으로 바뀌어 있어야 함
    assert results[0][4] == "최신 프로그램 (업데이트됨)"

def test_multiple_duplicates_in_one_batch(db_setup):
    """한 번에 여러 중복 데이터가 들어올 때의 처리 확인."""
    batch_data = [
        ("2026_03_26", "public", "KBS1", "10:00", "프로그램 A"),
        ("2026_03_26", "public", "KBS1", "10:00", "프로그램 B"), # 중복 (B가 남아야 함)
        ("2026_03_26", "public", "KBS1", "11:00", "프로그램 C")
    ]
    save_tv_guide(batch_data)
    
    results = get_filtered_guide(date="2026_03_26", channel="KBS1")
    assert len(results) == 2
    assert any(r[4] == "프로그램 B" for r in results)
    assert not any(r[4] == "프로그램 A" for r in results)
