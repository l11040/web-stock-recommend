from ..models.stock_model import KospiTop100

def get_all_stocks():
    return KospiTop100.query.all()
