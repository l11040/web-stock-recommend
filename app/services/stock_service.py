import time
import logging
from datetime import datetime, timedelta
from ..models.stock_model import StockData, StockCode
from ..db import db
import requests
from urllib import parse
from ast import literal_eval

# 종목 데이터 가져오는 함수
def get_sise(code, start_time, end_time, time_from='day'):
    get_param = {
        'symbol': code,
        'requestType': 1,
        'startTime': start_time,
        'endTime': end_time,
        'timeframe': time_from
    }
    get_param = parse.urlencode(get_param)
    url = f"https://api.finance.naver.com/siseJson.naver?{get_param}"
    response = requests.get(url)
    return literal_eval(response.text.strip())

# DB에 데이터 삽입
def insert_data_to_db(data):
    for row in data:
        stock_entry = StockData(
            date=row[0],  # 날짜
            stock_code=row[1],  # 종목 코드
            open_price=row[2],  # 시가
            high_price=row[3],  # 고가
            low_price=row[4],  # 저가
            close_price=row[5],  # 종가
            volume=row[6],  # 거래량
            foreign_ownership=row[7]  # 외국인 소진율
        )
        
        # DB에 삽입 (중복일 경우 업데이트)
        existing_entry = StockData.query.filter_by(date=row[0], stock_code=row[1]).first()
        if existing_entry:
            existing_entry.open_price = row[2]
            existing_entry.high_price = row[3]
            existing_entry.low_price = row[4]
            existing_entry.close_price = row[5]
            existing_entry.volume = row[6]
            existing_entry.foreign_ownership = row[7]
        else:
            db.session.add(stock_entry)
    
    db.session.commit()

# 스케줄 작업에 의해 호출될 함수
def fetch_and_store_stock_data(start_time, end_time):
    stock_codes = StockCode.query.all()
    top100_codes = [stock.code for stock in stock_codes]

    total_codes = len(top100_codes)  # 종목 코드의 총 수
    for idx, code in enumerate(top100_codes, start=1):
        # 로그 출력: 진행 상황
        logging.info(f"Processing {idx}/{total_codes}: {code}")

        data = get_sise(code, start_time, end_time, 'day')
        # API 요청 후 1초 대기
        time.sleep(1)
        daily_data = []

        for row in data[1:]:  # 첫 번째 행은 헤더이므로 제외
            parsed_row = [
                datetime.strptime(row[0], "%Y%m%d").date(),  # 날짜를 Date 형식으로 변환
                code,               # 종목 코드
                row[1],             # 시가
                row[2],             # 고가
                row[3],             # 저가
                row[4],             # 종가
                row[5],             # 거래량
                row[6]              # 외국인 소진율
            ]
            daily_data.append(parsed_row)
        
        insert_data_to_db(daily_data)

        # 로그 출력: 해당 종목 완료
        logging.info(f"Completed {code}")

def get_all_stocks():
    return StockCode.query.all()

def get_recent_stock_data(days: int):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    # 최근 n일간의 주식 데이터를 필터링하여 가져옴
    stock_data = StockData.query.filter(
        StockData.date >= start_date,
        StockData.date <= end_date
    ).all()

    return stock_data