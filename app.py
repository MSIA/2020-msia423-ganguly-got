import traceback
from flask import render_template, request, redirect, url_for
import logging.config
from flask import Flask

from flask_sqlalchemy import SQLAlchemy

# Initialize the Flask application
app = Flask('GOT_Simulator_App', template_folder="app/templates", static_folder="app/static")

# Configure flask app from flask_config.py
app.config.from_pyfile('config/flaskconfig.py')

# Define LOGGING_CONFIG in flask_config.py - path to config file for setting
# up the logger (e.g. config/logging/local.conf)
logging.config.fileConfig(app.config["LOGGING_CONFIG"])
logger = logging.getLogger(app.config["APP_NAME"])
logger.debug('Test log')

from src.create_score_db import got_prediction
# Initialize the database
db = SQLAlchemy(app)
logger.info("database string: " + str(db))


@app.route('/')
def index():
    """Main view of web page.
    Create view into index page that uses data queried from got_prediction database and
    inserts it into the app/templates/index.html template.
    Returns: rendered html template
    """

    try:
        predictions = db.session.query(got_prediction).limit(1)
        logger.debug("Index page accessed")
        return render_template('index.html', predictions=predictions)
    except:
        traceback.print_exc()
        logger.warning("Not able to display predictions, error page returned")
        return render_template('error.html')


@app.route('/add', methods=['POST'])
def add_entry():
    """View that queries database with user inputs and renders survival prediction
    :return: redirect to index page
    """

    try:
        # accesses user inputs from request.form
        Gender = request.form['Gender']
        Nobility = request.form['Nobility']
        boolDeadRelations = request.form['boolDeadRelations']
        isPopular = request.form['isPopular']
        isMarried = request.form['isMarried']
        allegiance = request.form['Allegiance']

        # converts request.form inputs to integer for querying
        if Gender == '1': Gender = 1
        else: Gender = 0
        if Nobility == '1': Nobility = 1
        else: Nobility = 0
        if boolDeadRelations == '1': boolDeadRelations = 1
        else: boolDeadRelations = 0
        if isPopular == '1': isPopular = 1
        else: isPopular = 0
        if isMarried == '1': isMarried = 1
        else: isMarried = 0

        # convert 'Allegiance' to dummy variables
        if allegiance == 'Baratheon':
            HouseBaratheon = 1
            HouseLannister = HouseStark = HouseTargaryen = NightsWatch = Wildling = 0
        elif allegiance == 'Lannister':
            HouseLannister = 1
            HouseBaratheon = HouseStark = HouseTargaryen = NightsWatch = Wildling = 0
        elif allegiance == 'Stark':
            HouseStark = 1
            HouseBaratheon = HouseLannister = HouseTargaryen = NightsWatch = Wildling = 0
        elif allegiance == 'Targaryen':
            HouseTargaryen = 1
            HouseBaratheon = HouseLannister = HouseStark = NightsWatch = Wildling = 0
        elif allegiance == "Night's Watch":
            NightsWatch = 1
            HouseBaratheon = HouseLannister = HouseStark = HouseTargaryen = Wildling = 0
        elif allegiance == 'Wildling':
            Wildling = 1
            HouseBaratheon = HouseLannister = HouseStark = HouseTargaryen = NightsWatch = 0

        # obtaining prediction by querying got_prediction with user inputs
        pred = db.session.query(got_prediction).filter(got_prediction.Gender == Gender,
                                                       got_prediction.Nobility == Nobility,
                                                       got_prediction.boolDeadRelations == boolDeadRelations,
                                                       got_prediction.isPopular == isPopular,
                                                       got_prediction.isMarried == isMarried,
                                                       got_prediction.HouseBaratheon == HouseBaratheon,
                                                       got_prediction.HouseLannister == HouseLannister,
                                                       got_prediction.HouseStark == HouseStark,
                                                       got_prediction.HouseTargaryen == HouseTargaryen,
                                                       got_prediction.NightsWatch == NightsWatch,
                                                       got_prediction.Wildling == Wildling)
        logger.info("New prediction generated for user in House : %s", request.form['Allegiance'])
        return render_template('index.html', predictions=pred)
    except:
        logger.warning("Not able to display predictions, error page returned")
        return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"], host=app.config["HOST"])