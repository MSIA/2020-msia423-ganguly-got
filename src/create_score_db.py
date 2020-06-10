import os
import logging
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlalchemy.exc
from sqlalchemy import create_engine, Column, Integer, String, Text

# Logging
logger = logging.getLogger(__name__)

Base = declarative_base()


# ORM mapping class for SQLAlchemy table 'prediction'
class got_prediction(Base):
    """Create a data model for the database to be set up for capturing offline predictions """
    __tablename__ = 'got_prediction'
    id = Column(Integer, primary_key=True)
    Gender = Column(Integer, unique=False, nullable=False)
    Nobility = Column(Integer, unique=False, nullable=False)
    boolDeadRelations = Column(Integer, unique=False, nullable=False)
    isPopular = Column(Integer, unique=False, nullable=False)
    isMarried = Column(Integer, unique=False, nullable=False)
    HouseBaratheon = Column(Integer, unique=False, nullable=False)
    HouseLannister = Column(Integer, unique=False, nullable=False)
    HouseStark = Column(Integer, unique=False, nullable=False)
    HouseTargaryen = Column(Integer, unique=False, nullable=False)
    NightsWatch = Column(Integer, unique=False, nullable=False)
    Wildling = Column(Integer, unique=False, nullable=False)
    score = Column(Integer, unique=False, nullable=False)
    prediction = Column(String(100), unique=False, nullable=False)
    remarks = Column(Text(100), unique=False, nullable=False)

    def __repr__(self):
        return '<got_prediction %s>' % self.prediction


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
            logger.info("create_db: %s created", engine_string)
        except sqlalchemy.exc.OperationalError:
            # Checking for correct credentials
            logger.error("create_db: Access denied! Please enter correct credentials")


def _truncate_prediction(session):
    """Deletes prediction table if rerunning and run into unique key error."""
    session.execute('''DELETE FROM got_prediction''')
    session.execute('''DROP TABLE got_prediction''')


def add_row(session, Gender, Nobility, boolDeadRelations, isPopular, isMarried, HouseBaratheon,
            HouseLannister, HouseStark, HouseTargaryen, NightsWatch, Wildling, score, prediction, remarks):
    """Adds rows to the prediction table

    Arguments:
        session: SQL session created for db
        id: Primary key
        Gender, Nobility, boolDeadRelations, isPopular, isMarried, HouseBaratheon,
        HouseLannister, HouseStark, HouseTargaryen, NightsWatch, Wildling: Input variables
        score: predicted class from model
        prediction: predicted survival category
        remarks: remark based on predicted survival category

    Returns:
        None
    """
    row = got_prediction(Gender=Gender, Nobility=Nobility, boolDeadRelations=boolDeadRelations,
                         isPopular=isPopular, isMarried=isMarried, HouseBaratheon=HouseBaratheon,
                         HouseLannister=HouseLannister, HouseStark=HouseStark, HouseTargaryen=HouseTargaryen,
                         NightsWatch=NightsWatch, Wildling=Wildling, score=score, prediction=prediction,
                         remarks=remarks)
    session.add(row)


def create_score_db(score_df, truncate, LOCAL_DATABASE_URI=None):
    """
    Creates database in configurable location and uploads offline scored data to table
    1. if environment variable SQLALCHEMY_DB_URI is defined - database created with this connection string
    2. if MYSQL details are provided - database created in RDS using connection string
    3. else - database created in LOCAL_DATABASE_URI defined in config/model_config.yaml

    Arguments:
        score_df: offline scored dataFrame from offline_score.csv
        truncate: to truncate existing table or not (0,1)
        LOCAL_DATABASE_URI: default location to create database if environment variables not specified

    Returns:
        None
    """
    logger.info("Truncate option = %d", truncate)
    # SQL/RDS connection string
    conn_type = "mysql+pymysql"
    user = os.environ.get("MYSQL_USER")
    password = os.environ.get("MYSQL_PASSWORD")
    host = os.environ.get("MYSQL_HOST")
    port = os.environ.get("MYSQL_PORT")
    database = os.environ.get("DATABASE_NAME")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    print(SQLALCHEMY_DATABASE_URI)

    if SQLALCHEMY_DATABASE_URI is not None:
        pass
    elif host is None:
        SQLALCHEMY_DATABASE_URI = LOCAL_DATABASE_URI
    else:
        SQLALCHEMY_DATABASE_URI = "{}://{}:{}@{}:{}/{}".format(conn_type, user, password, host, port, database)

    logger.info("Engine string used: %s", SQLALCHEMY_DATABASE_URI)

    # truncate existing table 'got_prediction' if -t specified in docker run command
    if truncate == 1:
        logger.info("truncate loop entered")
        engine = sql.create_engine(SQLALCHEMY_DATABASE_URI)
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
    create_db(engine_string=SQLALCHEMY_DATABASE_URI)

    # add rows to table 'got_prediction'
    try:
        logger.info("Database creation initiated. Expected time to finish: 1-2 minutes.")
        engine = sql.create_engine(SQLALCHEMY_DATABASE_URI)
        Session = sessionmaker(bind=engine)
        session = Session()

        successful_add = 0
        for index, row in score_df.iterrows():
            add_row(session, Gender=row['Gender'], Nobility=row['Nobility'],
                    boolDeadRelations=row['boolDeadRelations'], isPopular=row['isPopular'],
                    isMarried=row['isMarried'], HouseBaratheon=row['HouseBaratheon'],
                    HouseLannister=row['HouseLannister'], HouseStark=row['HouseStark'],
                    HouseTargaryen=row['HouseTargaryen'], NightsWatch=row['NightsWatch'],
                    Wildling=row['Wildling'], score=row['score'], prediction=row['prediction'],
                    remarks=row['remarks'])
            logger.debug("One row added to prediction table for id = %d", row['id'])
            successful_add += 1
        session.commit()
        logger.info("Database created with %d rows", successful_add)
    except sqlalchemy.exc.IntegrityError as e:
        # Checking for primary key duplication
        logger.error("add_row: " + str(e))
    except sqlalchemy.exc.OperationalError:
        # Checking for correct credentials
        logger.error("add_row: Access denied! Please enter correct credentials")
    finally:
        session.close()