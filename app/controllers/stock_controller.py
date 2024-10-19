from flask import Blueprint, jsonify
from ..services.stock_service import get_all_stocks

stock_bp = Blueprint('stocks', __name__)

@stock_bp.route('/', methods=['GET'])
def get_stocks():
    stocks = get_all_stocks()
    return jsonify([{'Code': stock.Code, 'Name': stock.Name} for stock in stocks])
