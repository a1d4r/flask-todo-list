from pathlib import Path
from typing import Optional

from pydantic import BaseSettings, Field

base_dir = Path(__file__).resolve(strict=True).parent


class GlobalConfig(BaseSettings):
    SECRET_KEY: str = Field('not a secret key', env='SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    TASKS_PER_PAGE: int = 10
    FLASK_CONFIG: str = Field('development', env='FLASK_CONFIG')
    # in-memory database
    SQLALCHEMY_DATABASE_URI: str = Field('sqlite://', env='DEV_DATABASE_URL')


class DevelopmentConfig(GlobalConfig):
    DEBUG: bool = True
    # db.sqlite in project folder
    SQLALCHEMY_DATABASE_URI: str = Field(
        'sqlite:///' + str(base_dir.parent / 'db.sqlite'), env='DEV_DATABASE_URL'
    )


class TestingConfig(GlobalConfig):
    TESTING: bool = True


class ProductionConfig(GlobalConfig):
    pass


class FactoryConfig:
    """Returns a config instance depending on the FLASK_CONFIG variable."""

    def __init__(self, config_name: Optional[str]):
        self.config_name = config_name

    def __call__(self):
        return {
            'development': DevelopmentConfig,
            'testing': TestingConfig,
            'production': ProductionConfig,
        }.get(self.config_name, DevelopmentConfig)()
