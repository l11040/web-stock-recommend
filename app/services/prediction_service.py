from ..models.prediction_model import PredictedStock
from ..db import db
from datetime import datetime

def save_predictions_to_db(stock_predictions):
    today = datetime.now().date()
    
    for stock_code, predicted_price, change_percent in stock_predictions:
        print(f"Saving: {stock_code}, {predicted_price}, {change_percent}")  # 로그 출력

        existing_entry = PredictedStock.query.filter_by(date=today, stock_code=stock_code).first()

        if existing_entry:
            existing_entry.predicted_price = predicted_price
            existing_entry.change_percent = change_percent
        else:
            new_prediction = PredictedStock(
                date=today,
                stock_code=stock_code,
                predicted_price=predicted_price,
                change_percent=change_percent
            )
            db.session.add(new_prediction)

    db.session.commit()

