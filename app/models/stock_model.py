from ..db import db

class KospiTop100(db.Model):
    __tablename__ = 'kospi_top100'
    Code = db.Column(db.String(10), primary_key=True)
    Name = db.Column(db.String(255), nullable=False)

    def __init__(self, Code, Name):
        self.Code = Code
        self.Name = Name
