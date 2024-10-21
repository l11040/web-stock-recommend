from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from ..services.stock_service import fetch_and_store_stock_data

# 스케줄 작업 함수
def scheduled_job():
    print("스케줄 작업 실행 중")
    today = datetime.now().strftime('%Y%m%d')
    # 종목 데이터를 파싱하고 DB에 저장하는 서비스 호출
    fetch_and_store_stock_data(today, today)

# 스케줄러 설정 및 시작
def start_scheduler():
    scheduler = BackgroundScheduler()
    # 평일 오후 11시에 작업을 실행하도록 스케줄 설정
    scheduler.add_job(scheduled_job, 'cron', day_of_week='mon-fri', hour=23, minute=0)
    scheduler.start()
