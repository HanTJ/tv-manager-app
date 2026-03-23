from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import subprocess
import logging
from database import log_job_status

# 로그 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scheduler")

def run_daily_scraping():
    """매일 0시에 실행되어 익일 편성표를 크롤링함."""
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y_%m_%d")
    logger.info(f"--- 정기 스케줄 실행: {tomorrow} 전체 데이터 크롤링 시작 ---")
    
    try:
        # main.py를 서브프로세스로 실행
        result = subprocess.run(["uv", "run", "main.py", tomorrow, "all"], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"정기 스케줄 완료: {tomorrow} 데이터 적재 성공.")
            log_job_status("Daily Scrape", tomorrow, "SUCCESS", "정상 완료")
        else:
            error_msg = result.stderr if result.stderr else "알 수 없는 오류"
            logger.error(f"정기 스케줄 실패: {error_msg}")
            log_job_status("Daily Scrape", tomorrow, "FAILED", error_msg[:200])
            
    except Exception as e:
        logger.error(f"정기 스케줄 도중 시스템 오류 발생: {e}")
        log_job_status("Daily Scrape", tomorrow, "FAILED", str(e)[:200])

def start_scheduler():
    """백그라운드 스케줄러 시작."""
    scheduler = BackgroundScheduler()
    # 매일 00:00:05 에 실행
    scheduler.add_job(run_daily_scraping, 'cron', hour=0, minute=0, second=5)
    
    scheduler.start()
    logger.info("Background Scheduler started (Scheduled for 00:00 daily).")
    return scheduler
