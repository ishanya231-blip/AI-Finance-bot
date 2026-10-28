from flask import Flask
from .models import db
from .routes import api_bp


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-personal-finance-bot'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///personal_finance.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    app.register_blueprint(api_bp)
    return app


app = create_app()