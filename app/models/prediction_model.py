from ..db import db
from datetime import date

class PredictedStock(db.Model):
    __tablename__ = 'predicted_stock'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    stock_code = db.Column(db.String(10), nullable=False)
    predicted_price = db.Column(db.Float, nullable=False)
    change_percent = db.Column(db.Float, nullable=False)  # 예측 가격 상승률
    __table_args__ = (
        db.UniqueConstraint('date', 'stock_code', name='_predicted_data_uc'),
    )

    def __init__(self, date: date, stock_code: str, predicted_price: float, change_percent: float):
        self.date = date
        self.stock_code = stock_code
        self.predicted_price = predicted_price
        self.change_percent = change_percent
