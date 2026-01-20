import os
from pathlib import Path

class Config:
    """Base configuration"""
    BASE_DIR = Path(__file__).parent
    SECRET_KEY = "806d6fd2258bebaaf4c1f91f5c2b4bcbad904f8357b764afe9779a0af60c22fc"
    DATABASE = os.path.join(BASE_DIR, 'mood_activities.db')
    DEBUG = True
    TESTING = False
    ACTIVITIES_PER_PAGE = 12


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    # Using the same hardcoded secret key
    SECRET_KEY = "806d6fd2258bebaaf4c1f91f5c2b4bcbad904f8357b764afe9779a0af60c22fc"


class TestingConfig(Config):
    TESTING = True
    DATABASE = ':memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
