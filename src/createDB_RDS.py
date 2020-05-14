import os
import config
import logging.config
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import argparse

import sqlalchemy.exc

from sqlalchemy import create_engine, Column, Integer, String, Text

Base = declarative_base()

# ORM mapping class for SQLAlchemy table 'prediction'
class prediction(Base):
    """Create a data model for the database to be set up for capturing offline predictions """
    __tablename__ = 'prediction'
    id = Column(Integer, primary_key=True)
    house = Column(String(100), unique=False, nullable=False)
    nobility = Column(String(100), unique=False, nullable=False)
    gender = Column(String(100), unique=False, nullable=False)
    profession = Column(String(100), unique=False, nullable=False)
    survival = Column(Integer, unique=False, nullable=False)

    def __repr__(self):
        pred_repr = "<prediction(id='%d', house='%s', nobility='%s', gender='%s', profession='%s', survival='%d')>"
        return pred_repr % (self.id, self.house, self.nobility, self.gender, self.profession, self.survival)


# Logging
logging_config = 'config/logging/local.conf'

logging.config.fileConfig(logging_config)
logger = logging.getLogger('createDB_RDS')

# SQL/RDS connection string
conn_type = "mysql+pymysql"
user = os.environ.get("MYSQL_USER")
password = os.environ.get("MYSQL_PASSWORD")
host = os.environ.get("MYSQL_HOST")
port = os.environ.get("MYSQL_PORT")
database = os.environ.get("DATABASE_NAME")

if config.CREATE_DB_LOCALLY is True:
    # Create database in local SQLite
    engine_string = config.SQLALCHEMY_DATABASE_URI
else:
    # Create database in RDS
    engine_string = "{}://{}:{}@{}:{}/{}".format(conn_type, user, password, host, port, database)


def create_db(engine_string):
    """Creates a database with the data models inherited from `Base` (Prediction).

    Args:
        engine_string (`str`, default None): String defining SQLAlchemy connection URI in the form of
            `dialect+driver://username:password@host:port/database` or
            'sqlite:///path_to_db' for creating local SQLite database

    Returns:
        ValueError if engine_string is not provided
        None otherwise
    """
    if engine_string is None:
        return ValueError("`engine_string` must be provided")
    else:
        try:
            engine = sql.create_engine(engine_string)
            Base.metadata.create_all(engine)
            logger.info("create_db: %s created",engine_string)
        except sqlalchemy.exc.OperationalError:
            # Checking for correct credentials
            logger.error("create_db: Access denied! Please enter correct credentials")



def _truncate_prediction(session):
    """Deletes prediction table if rerunning and run into unique key error."""
    session.execute('''DELETE FROM prediction''')

def add_row(session, id, house, nobility, gender, profession, survival):
    """Adds rows to the prediction table

    Args:
        session = SQL session created for db
        id = Primary key
        house, nobility, gender, profession = Input variables
        survival = Survival prediction

    Returns:
        None
    """
    row = prediction(id=id, house=house, nobility=nobility, gender=gender, profession=profession, survival=survival)
    session.add(row)
    session.commit()
    logger.info("One row added to prediction table for id = %d",id)


if __name__ == "__main__":

    # Giving user option to delete 'prediction' table and repopulate
    parser = argparse.ArgumentParser(description="Create defined tables in database")
    parser.add_argument("--truncate", "-t", default=False, action="store_true",
                        help="If given, delete current records from prediction table before create_all "
                             "so that table can be recreated without unique id issues ")
    args = parser.parse_args()

    # If "truncate" is given as an argument (i.e. python src/createDB_RDS.py --t), then empty the prediction table
    if args.truncate:
        engine = sql.create_engine(engine_string)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            logger.info("Attempting to truncate prediction table.")
            _truncate_prediction(session)
            session.commit()
            session.close()
            logger.info("prediction truncated.")
        except Exception as e:
            logger.error("Error occurred while attempting to truncate prediction table.")
            logger.error(e)
        finally:
            session.close()

    # Create database
    create_db(engine_string=engine_string)

    # Add row to table 'prediction'
    try:
        engine = sql.create_engine(engine_string)
        Session = sessionmaker(bind=engine)
        session = Session()
        add_row(session, id=123, house="cde", nobility="efg", gender="abc", profession="jh", survival=9)
        logger.info("Database created with one dummy row")
    except sqlalchemy.exc.IntegrityError as e:
        # Checking for primary key duplication
        logger.error("add_row: "+str(e.args))
    except sqlalchemy.exc.OperationalError:
        # Checking for correct credentials
        logger.error("add_row: Access denied! Please enter correct credentials")
    finally:
        session.close()