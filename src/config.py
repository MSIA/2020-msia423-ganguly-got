from os import path

# Getting the parent directory of this file. That will function as the project home.
PROJECT_HOME = path.dirname(path.dirname(path.abspath(__file__)))

""" S3 configurations """
# The physical location of the raw data file to be put in S3 bucket
RAW_DATA_FILE = path.join(PROJECT_HOME,'data/external/character-deaths.csv')
FILE_NAME = "character-deaths.csv"

# Logging
LOGGING_CONFIG = path.join(PROJECT_HOME, 'config/logging/logging.conf')

# Configurable name of S3 bucket
S3_BUCKET = "msia423-project"

""" RDS configurations """
# Configurable variable to decide if DB to be created in SQLite or RDS
CREATE_DB_LOCALLY = False

# Location for creating local SQLITE database
DATABASE_PATH = path.join(PROJECT_HOME, 'data/msia423_project_db.db')
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DATABASE_PATH)
