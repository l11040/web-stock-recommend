from ..db import db

class StockCode(db.Model):
    __tablename__ = 'kospi_top100'
    code = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __init__(self, code, name):
        self.code = code
        self.name = name

from ..db import db

class StockData(db.Model):
    __tablename__ = 'stock_data'
    date = db.Column(db.Date, nullable=False, primary_key=True)
    stock_code = db.Column(db.String(10), nullable=False, primary_key=True)
    open_price = db.Column(db.Float)
    high_price = db.Column(db.Float)
    low_price = db.Column(db.Float)
    close_price = db.Column(db.Float)
    volume = db.Column(db.BigInteger)
    foreign_ownership = db.Column(db.Float)

    def __init__(self, date, stock_code, open_price, high_price, low_price, close_price, volume, foreign_ownership):
        self.date = date
        self.stock_code = stock_code
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.close_price = close_price
        self.volume = volume
        self.foreign_ownership = foreign_ownership
