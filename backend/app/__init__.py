"""Flask application factory."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate

db = SQLAlchemy()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
migrate = Migrate()


def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__)

    from app.config import config_map
    app.config.from_object(config_map[config_name])

    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from app.routes.auth import auth_bp
    from app.routes.profile import profile_bp
    from app.routes.product import product_bp
    from app.routes.chat import chat_bp
    from app.routes.scan import scan_bp
    from app.routes.ai_analysis import ai_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(profile_bp, url_prefix="/api")
    app.register_blueprint(product_bp, url_prefix="/api")
    app.register_blueprint(chat_bp, url_prefix="/api")
    app.register_blueprint(scan_bp, url_prefix="/api")
    app.register_blueprint(ai_bp, url_prefix="/api")

    _register_swagger(app)

    return app


def _register_swagger(app: Flask) -> None:
    from flask_swagger_ui import get_swaggerui_blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        "/api/docs",
        "/api/swagger.json",
        config={"app_name": "Food Truth Teller API"},
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix="/api/docs")
