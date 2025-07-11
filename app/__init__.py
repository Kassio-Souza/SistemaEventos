from flask import Flask
from .config import Config
from .routes import init_routes

def create_app():
    app = Flask(__name__,static_folder='../static')
    app.config.from_object(Config)
    app.secret_key = app.config['SECRET_KEY']

    init_routes(app)  # importa e registra as rotas
    return app