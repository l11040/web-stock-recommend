from flask import Flask
from .db import db, migrate

def create_app():
    app = Flask(__name__)

    # Config 설정 로드
    app.config.from_object('config.Config')

    # 데이터베이스 초기화
    db.init_app(app)
    migrate.init_app(app, db)

    # 블루프린트 등록
    from .controllers.stock_controller import stock_bp
    app.register_blueprint(stock_bp, url_prefix='/stocks')

    return app