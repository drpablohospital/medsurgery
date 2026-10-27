import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'promocir-dev-secret-2026-change-in-prod'
    
    # Base de datos PostgreSQL - usando psycopg v3 (driver: postgresql+psycopg)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql+psycopg://promocir_app:promocir_secure_2026@localhost:5432/promocir'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Sesiones
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    
    # App
    APP_NAME = 'PromoCir'
    APP_VERSION = '1.0.0'
    
class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    # En producción, SECRET_KEY DEBE venir de variables de entorno

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
