# import os
# from pathlib import Path

# class Config:
#     """Base configuration"""
#     BASE_DIR = Path(__file__).parent
#     SECRET_KEY = "806d6fd2258bebaaf4c1f91f5c2b4bcbad904f8357b764afe9779a0af60c22fc"
#     DATABASE = os.path.join(BASE_DIR, 'mood_activities.db')
#     DEBUG = True
#     TESTING = False
#     ACTIVITIES_PER_PAGE = 12


# class DevelopmentConfig(Config):
#     DEBUG = True


# class ProductionConfig(Config):
#     DEBUG = False
    
#     SECRET_KEY = "806d6fd2258bebaaf4c1f91f5c2b4bcbad904f8357b764afe9779a0af60c22fc"


# class TestingConfig(Config):
#     TESTING = True
#     DATABASE = ':memory:'


# config = {
#     'development': DevelopmentConfig,
#     'production': ProductionConfig,
#     'testing': TestingConfig,
#     'default': DevelopmentConfig
# }


"""
MoodMatch Application Configuration
"""

import os

class Config:
    """Base configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'moodmatch-secret-key-change-in-production'
    
    # Database settings
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE = os.path.join(BASE_DIR, 'instance', 'moodmatch.db')
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Session settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # VADER Sentiment thresholds
    VADER_NEGATIVE_THRESHOLD = -0.2
    VADER_POSITIVE_THRESHOLD = 0.2
    
    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

# Default config
config = DevelopmentConfig