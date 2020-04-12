# MSiA 423 2020
## How long will you play the Game of Thrones?

 - Developer - Shreyashi Ganguly
 - Quality Assurance - Kristiyan Dimitrov

<!-- toc -->

- [Project Charter](#directory-structure)
- [Project Backlog](#directory-structure)
- [Directory structure](#directory-structure)
- [Running the app](#running-the-app)
  * [1. Initialize the database](#1-initialize-the-database)
    + [Create the database with a single song](#create-the-database-with-a-single-song)
    + [Adding additional songs](#adding-additional-songs)
    + [Defining your engine string](#defining-your-engine-string)
      - [Local SQLite database](#local-sqlite-database)
  * [2. Configure Flask app](#2-configure-flask-app)
  * [3. Run the Flask app](#3-run-the-flask-app)
- [Running the app in Docker](#running-the-app-in-docker)
  * [1. Build the image](#1-build-the-image)
  * [2. Run the container](#2-run-the-container)
  * [3. Kill the container](#3-kill-the-container)
  * [Workaround for potential Docker problem for Windows.](#workaround-for-potential-docker-problem-for-windows)

<!-- tocstop -->

## Project Charter
### Vision
To provide fans of the hit TV series Game of Thrones(GoT), based on the equally famous book series "A Song of Fire and Ice" by George RR Martin, a platform to interact with its vastly complicated and perilous fantasy world

### Mission
Develop an application that allows user to build his/her own character in the fantasy series GoT, by choosing responses to a set of questions. The application then outputs the expected life span of the user's character considering the survival of similar existing characters in the series.
**Data Source**: https://www.kaggle.com/mylesoneill/game-of-thrones

### Success Criteria
#### 1. Model Performance
The problem will be attempted via both regression and classification techniques. Accordingly the following performance metrics will be evaluated to assess success:

 - Classification - misclassification rate (<20%)
 - Regression - Mean Absolute Percentage Error (<20%)

#### 2. Business Outcome
The following set of metrics will be measured for tracking user engagement with the application

 - Number of visits to the app in an interval of time
 - Fraction of returning users
 - Average time spent on the app per visit

## Project Backlog
### Initiatives

 1. Develop benchmark supervised machine learning model to predict lifespan of existing GoT characters
 2. Iterate model by applying alternate ML techniques
 3. Design and develop the web application to deploy final model

### Epics and Stories
The initiatives defined above are broken down into major milestones (epics) which are further split into distinct pieces of work (stories). Stories are listed in descending order of priority or in order of execution. Each story is assigned points according to expected magnitude of work
-   0 points - quick chore
-   1 point ~ 1 hour (small)
-   2 points ~ 1/2 day (medium)
-   4 points ~ 1 day (large)

Stories that are not essential, but are good to have, are not sized and denoted as 'icebox'
**Initiative**: Develop benchmark model
 1. Prepare data for Machine Learning model development
 - [ ] Download datasets from Kaggle - 0
 - [ ] Identify overlap between datasets and merge relevant fields - 1
 - [ ] Identify gaps in the data and assess how to best fill them - 2
 - [ ] (icebox) Identify other external sources of information that might bring relevant insights

 2. Perform Exploratory Data Analysis
 - [ ] 

## Directory structure 

```
├── README.md                         <- You are here
├── api
│   ├── static/                       <- CSS, JS files that remain static
│   ├── templates/                    <- HTML (or other code) that is templated and changes based on a set of inputs
│   ├── boot.sh                       <- Start up script for launching app in Docker container.
│   ├── Dockerfile                    <- Dockerfile for building image to run app  
│
├── config                            <- Directory for configuration files 
│   ├── local/                        <- Directory for keeping environment variables and other local configurations that *do not sync** to Github 
│   ├── logging/                      <- Configuration of python loggers
│   ├── flaskconfig.py                <- Configurations for Flask API 
│
├── data                              <- Folder that contains data used or generated. Only the external/ and sample/ subdirectories are tracked by git. 
│   ├── external/                     <- External data sources, usually reference data,  will be synced with git
│   ├── sample/                       <- Sample data used for code development and testing, will be synced with git
│
├── deliverables/                     <- Any white papers, presentations, final work products that are presented or delivered to a stakeholder 
│
├── docs/                             <- Sphinx documentation based on Python docstrings. Optional for this project. 
│
├── figures/                          <- Generated graphics and figures to be used in reporting, documentation, etc
│
├── models/                           <- Trained model objects (TMOs), model predictions, and/or model summaries
│
├── notebooks/
│   ├── archive/                      <- Develop notebooks no longer being used.
│   ├── deliver/                      <- Notebooks shared with others / in final state
│   ├── develop/                      <- Current notebooks being used in development.
│   ├── template.ipynb                <- Template notebook for analysis with useful imports, helper functions, and SQLAlchemy setup. 
│
├── reference/                        <- Any reference material relevant to the project
│
├── src/                              <- Source data for the project 
│
├── test/                             <- Files necessary for running model tests (see documentation below) 
│
├── app.py                            <- Flask wrapper for running the model 
├── run.py                            <- Simplifies the execution of one or more of the src scripts  
├── requirements.txt                  <- Python package dependencies 
```

## Running the app
### 1. Initialize the database 

#### Create the database with a single song 
To create the database in the location configured in `config.py` with one initial song, run: 

`python run.py create_db --engine_string=<engine_string> --artist=<ARTIST> --title=<TITLE> --album=<ALBUM>`

By default, `python run.py create_db` creates a database at `sqlite:///data/tracks.db` with the initial song *Radar* by Britney spears. 
#### Adding additional songs 
To add an additional song:

`python run.py ingest --engine_string=<engine_string> --artist=<ARTIST> --title=<TITLE> --album=<ALBUM>`

By default, `python run.py ingest` adds *Minor Cause* by Emancipator to the SQLite database located in `sqlite:///data/tracks.db`.

#### Defining your engine string 
A SQLAlchemy database connection is defined by a string with the following format:

`dialect+driver://username:password@host:port/database`

The `+dialect` is optional and if not provided, a default is used. For a more detailed description of what `dialect` and `driver` are and how a connection is made, you can see the documentation [here](https://docs.sqlalchemy.org/en/13/core/engines.html). We will cover SQLAlchemy and connection strings in the SQLAlchemy lab session on 
##### Local SQLite database 

A local SQLite database can be created for development and local testing. It does not require a username or password and replaces the host and port with the path to the database file: 

```python
engine_string='sqlite:///data/tracks.db'

```

The three `///` denote that it is a relative path to where the code is being run (which is from the root of this directory).

You can also define the absolute path with four `////`, for example:

```python
engine_string = 'sqlite://///Users/cmawer/Repos/2020-MSIA423-template-repository/data/tracks.db'
```


### 2. Configure Flask app 

`config/flaskconfig.py` holds the configurations for the Flask app. It includes the following configurations:

```python
DEBUG = True  # Keep True for debugging, change to False when moving to production 
LOGGING_CONFIG = "config/logging/local.conf"  # Path to file that configures Python logger
HOST = "0.0.0.0" # the host that is running the app. 0.0.0.0 when running locally 
PORT = 5000  # What port to expose app on. Must be the same as the port exposed in app/Dockerfile 
SQLALCHEMY_DATABASE_URI = 'sqlite:///data/tracks.db'  # URI (engine string) for database that contains tracks
APP_NAME = "penny-lane"
SQLALCHEMY_TRACK_MODIFICATIONS = True 
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 100 # Limits the number of rows returned from the database 
```

### 3. Run the Flask app 

To run the Flask app, run: 

```bash
python app.py
```

You should now be able to access the app at http://0.0.0.0:5000/ in your browser.

## Running the app in Docker 

### 1. Build the image 

The Dockerfile for running the flask app is in the `app/` folder. To build the image, run from this directory (the root of the repo): 

```bash
 docker build -f app/Dockerfile -t pennylane .
```

This command builds the Docker image, with the tag `pennylane`, based on the instructions in `app/Dockerfile` and the files existing in this directory.
 
### 2. Run the container 

To run the app, run from this directory: 

```bash
docker run -p 5000:5000 --name test pennylane
```
You should now be able to access the app at http://0.0.0.0:5000/ in your browser.

This command runs the `pennylane` image as a container named `test` and forwards the port 5000 from container to your laptop so that you can access the flask app exposed through that port. 

If `PORT` in `config/flaskconfig.py` is changed, this port should be changed accordingly (as should the `EXPOSE 5000` line in `app/Dockerfile`)

### 3. Kill the container 

Once finished with the app, you will need to kill the container. To do so: 

```bash
docker kill test 
```

where `test` is the name given in the `docker run` command.

### Workaround for potential Docker problem for Windows.

It is possible that Docker will have a problem with the bash script `app/boot.sh` that is used when running on a Windows machine. Windows can encode the script wrongly so that when it copies over to the Docker image, it is corrupted. If this happens to you, try using the alternate Dockerfile, `app/Dockerfile_windows`, i.e.:

```bash
 docker build -f app/Dockerfile_windows -t pennylane .
```

then run the same `docker run` command: 

```bash
docker run -p 5000:5000 --name test pennylane
```

The new image defines the entry command as `python3 app.py` instead of `./boot.sh`. Building the sample PennyLane image this way will require initializing the database prior to building the image so that it is copied over, rather than created when the container is run. Therefore, please **do the step [Create the database with a single song](#create-the-database-with-a-single-song) above before building the image**.
<!--stackedit_data:
eyJoaXN0b3J5IjpbNjgxNjk2MTY2LC0xMjYzMzQzODE0LC0xMz
czNzE4MzUsLTEyODI4OTgwMjUsNDk3Mjg3NjkyLC0yOTQwNDEw
NzQsMTkxOTMxNzAwMl19
-->