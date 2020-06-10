import os
import logging
logger = logging.getLogger(__name__)
DEBUG = False
LOGGING_CONFIG = "config/logging/local.conf"
PORT = 5000
APP_NAME = "GOT_Simulator_App"
SQLALCHEMY_TRACK_MODIFICATIONS = True
HOST = "0.0.0.0"
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 100

# Connection string
conn_type = "mysql+pymysql"
user = os.environ.get("MYSQL_USER")
password = os.environ.get("MYSQL_PASSWORD")
host = os.environ.get("MYSQL_HOST")
port = os.environ.get("MYSQL_PORT")
database = os.environ.get("DATABASE_NAME")
SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DB_URI")

if SQLALCHEMY_DATABASE_URI is not None:
    pass
elif host is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data/msia423_project_db.db'
else:
    SQLALCHEMY_DATABASE_URI = "{}://{}:{}@{}:{}/{}".format(conn_type, user, password, host, port, database)
