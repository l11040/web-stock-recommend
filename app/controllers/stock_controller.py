from flask import Blueprint, jsonify
from datetime import datetime, timedelta
from ..services.stock_service import get_all_stocks,fetch_and_store_stock_data

stock_bp = Blueprint('stocks', __name__)

@stock_bp.route('/', methods=['GET'])
def get_stocks():
    stocks = get_all_stocks()
    return jsonify([{'code': stock.code, 'name': stock.name} for stock in stocks])

@stock_bp.route('/fetch-stocks', methods=['GET'])
def fetch_stocks():
    # 오늘 날짜와 100일 전 날짜 계산
    end_time = datetime.now().strftime('%Y%m%d')
    start_time = (datetime.now() - timedelta(days=100)).strftime('%Y%m%d')

    # 100일치 데이터를 파싱하고 DB에 저장하는 함수 호출
    fetch_and_store_stock_data(start_time, end_time)

    return jsonify({"message": "100 days of stock data fetched and stored."})