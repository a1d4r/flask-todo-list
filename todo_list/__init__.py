from typing import Optional

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

from .config import FactoryConfig, GlobalConfig

bootstrap = Bootstrap()
db = SQLAlchemy()


def create_app(config_name: Optional[str] = None):
    """Create app with the specified config. (or env FLASK_CONFIG if ommited)"""
    app = Flask(__name__)
    config_name = config_name or GlobalConfig().FLASK_CONFIG
    config = FactoryConfig(config_name)()
    app.config.from_object(config)

    bootstrap.init_app(app)
    db.init_app(app)

    from .views import bp

    app.register_blueprint(bp)

    return app
