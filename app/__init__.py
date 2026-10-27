from flask import Flask
from flask_login import LoginManager
from app.config import config
from app.models import db, Usuario
import os

login_manager = LoginManager()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'warning'
    
    # Registrar blueprints
    from app.routes.auth import bp as auth_bp
    from app.routes.dashboard import bp as dashboard_bp
    from app.routes.visitas import bp as visitas_bp
    from app.routes.admin import bp as admin_bp
    from app.routes.api import bp as api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(visitas_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    
    # Headers de seguridad
    @app.after_request
    def add_security_headers(response):
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self'; media-src 'self'; frame-src 'self';"
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    # Filtros Jinja
    from app.utils.helpers import format_currency, format_datetime
    app.jinja_env.filters['currency'] = format_currency
    app.jinja_env.filters['datetime'] = format_datetime
    
    return app

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))
