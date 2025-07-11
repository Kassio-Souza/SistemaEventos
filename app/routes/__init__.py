from .index import index_bp
from .pessoa_routes import pessoa_bp
from .evento_routes import evento_bp
from .inscricao_routes import inscricao_bp
from .certificados_routes import certificados_bp

def init_routes(app):
    app.register_blueprint(index_bp)
    app.register_blueprint(pessoa_bp, url_prefix='/pessoa')
    app.register_blueprint(evento_bp, url_prefix='/evento')
    app.register_blueprint(inscricao_bp, url_prefix='/inscricao')
    app.register_blueprint(certificados_bp, url_prefix='/certificados')
