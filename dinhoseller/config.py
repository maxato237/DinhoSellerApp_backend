import os

DISTANT_DB_CONNEXION = {
    'host': 'bllkz2rubsr6lxqhlttx-mysql.services.clever-cloud.com',
    'user': 'usbqefhqtsll6nh6',
    'password': 'AbOmXp99etO4zgXBZxH9',
    'database': 'bllkz2rubsr6lxqhlttx',
    'port': '3306'
}

SQL_CONNEXION = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'dinhosellerbd',
    'port': '3306'
}


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'PO2RxQLMzAMAnIZfRYbVtR8yfPPbfBSJ'
    SECRET_JWT_KEY = "0ee06252f7b14d3ea2463pf9d4s65j41"
    DEBUG = True 

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{SQL_CONNEXION['user']}:{SQL_CONNEXION['password']}@{SQL_CONNEXION['host']}/{SQL_CONNEXION['database']}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DISTANT_DB_CONNEXION['user']}:{DISTANT_DB_CONNEXION['password']}@{DISTANT_DB_CONNEXION['host']}/{DISTANT_DB_CONNEXION['database']}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False