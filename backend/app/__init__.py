from flask import Flask
from .config import Config
from .db import db
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# Blueprints
from app.routes.auth_routes import auth_bp
from app.routes.inventory_routes import inventory_bp
from app.routes.billing_routes import billing_bp
from app.routes.analytics_routes import analytics_bp
from app.routes.ai_routes import ai_bp
from app.routes.chatbot_routes import chatbot_bp
from app.routes.dashboard_routes import dashboard_bp
from app.routes.monitoring_routes import monitoring_bp
from app.routes.alert_routes import alert_bp
from app.routes.device_routes import device_bp
from app.routes.sensor_routes import sensor_bp

from app.middleware import register_error_handlers

migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS
    CORS(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Register error handlers
    register_error_handlers(app)

    # IMPORTANT: Load models (for migrations)
    from app import models

    # Register Blueprints
    app.register_blueprint(chatbot_bp, url_prefix="/chatbot")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")
    app.register_blueprint(billing_bp, url_prefix="/billing")
    app.register_blueprint(analytics_bp, url_prefix="/analytics")
    app.register_blueprint(ai_bp, url_prefix="/ai")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(monitoring_bp, url_prefix="/monitoring")
    app.register_blueprint(alert_bp, url_prefix="/alerts")
    app.register_blueprint(device_bp, url_prefix="/devices")
    app.register_blueprint(sensor_bp, url_prefix="/sensors")

    return app
