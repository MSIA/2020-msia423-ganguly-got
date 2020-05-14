# MSiA 423 2020
## How long will you play the Game of Thrones?

 - Developer - Shreyashi Ganguly
 - Quality Assurance - Kristiyan Dimitrov

<!-- toc -->

- [Project Charter](#project-charter)
- [Project Backlog](#project-backlog)
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

## Running the data ingestion pipeline
### Step 1. Acquire data
Download the data from the following location

- Data source:  https://www.kaggle.com/mylesoneill/game-of-thrones
- Filename: character-deaths.csv

The file has been downloaded and stored in `data/external` folder. User can choose to use the same file for the subsequent steps, in which case there is no need to download again. Otherwise the file needs to be downloaded and placed in `data/external`. Please do not change the file name.

**NOTE: You will need to be on the Northwestern VPN for the subsequent steps*

### Step 1. Updating src/config.py
`src/config.py` contains all the configurable details about the data ingestion pipeline. All options can be used as is with their default values or user can choose to update them as needed.

 - `S3_BUCKET` - specify the name of the S3 bucket for storing the csv file
 - `CREATE_DB_LOCALLY` - specify `False` to create RDS database, `True` to create local SQLite database. Defaulted to `False`
 
 If `CREATE_DB_LOCALLY=True`, update the following in `src/config.py`
 
 - `DATABASE_PATH` - location where SQLite database must be stored. Defaulted to `/app/data/msia423_project_db.db`

Proceed to Step 2.

 If `CREATE_DB_LOCALLY=False`, 
 - update the AWS RDS details in `.mysqlconfig` as follows, 

Enter `vi .mysqlconfig`
		- Set `MYSQL_USER` to the “master username” that you used to create the database server
		- Set `MYSQL_PASSWORD` to the “master password” that you used to create the database server
		- Set `MYSQL_HOST` to be the RDS instance endpoint from the console
		- Set  `MYSQL_HOST` to be 3306
Again all the details are given default values which can be left unchanged.Set
		- Set `DATABASE_NAME` to be the desired name for the database
 - Set the environment variables in your ~/.bashrc,

     `echo 'source .mysqlconfig'>>~/.bashrc`
     `source ~/.bashrc`

### Step 2. Build docker image

    docker build -t got_image .

### Step 3. Write raw data to S3 bucket
Run the following command with your AWS credentials

    docker run -e AWS_ACCESS_KEY_ID=<aws_key> -e AWS_SECRET_ACCESS_KEY=<aws_secret_key> got_image src/write_to_s3.py

The file character-death.csv is now written to the S3 bucket!

### Step 4. Creating database for model serving
 -  Case 1: `CREATE_DB_LOCALLY=True` (creating local SQLite database)
```bash
docker run --mount type=bind,source="$(pwd)"/data,target=/app/data got_image src/createDB_RDS.py
```
 - Case 2: `CREATE_DB_LOCALLY=False` (creating AWS RDS database)
```bash
sh run_docker.sh
```
The database with the 'prediction' table has been created in SQLite/RDS with a dummy row.

***Note: If recreating the database add --t at the end of option1 and in run_docker.sh file for option2 to avoid IntegrityErrors due to duplicate records*

### Verifying database creation
If database is created in local SQLite, the same can be viewed/queried through applications like `DB Browser for SQLite`

If the database is created in RDS, it can be queried as follows,

 - Start MySQL client
 `sh run_mysql_client.sh` 
- To show databases
 `mysql> show databases;` 
 - To show tables
 `mysql> show tables from msia423_project_db;
` 
- Select rows from table
 `mysql> select * from msia423_project_db.prediction;
` 


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

Stories that are not essential immediately, but are good to have, are not sized and denoted with 'icebox'

**Initiative**: Develop benchmark model

 **Epic**: Prepare data for Machine Learning model development
 - [ ] Download datasets from Kaggle - 0
 - [ ] Identify overlap between datasets and merge relevant fields - 1
 - [ ] Identify gaps in the data and assess how to best fill them - 2
 - [ ] *(icebox)* Identify other external sources of information that might bring relevant insights

 **Epic**: Perform Exploratory Data Analysis
 - [ ] Investigate univariate distribution of each of the fields - 2
 - [ ] Examine bivariate relationships between features - 1
 - [ ] Design suitable target variable for both classification and regression approaches - 2
 - [ ] Explore expected lifespan of characters from particular segments - 2
 - [ ] Transform existing features into suitable form - 2
 - [ ] Remove redundant or repetitive features - 1
 - [ ] Record insights obtained during EDA to feed into future iterations - 1

**Epic**: Train and assess benchmark model
 - [ ] Split data into train and test samples - 1
 - [ ] Decide if regression or classification should be the benchmark model - 0
 - [ ] Decide performance evaluation criteria to be used - 2
 - [ ] Train model on training data - 2
 - [ ] Evaluate performance on test data and record - 2

**Initiative**: Iterate with other suitable ML techniques

**Epic**: Improve model using alternative ML techniques and engineering newer features
 - [ ] Research and identify other relevant supervised modeling techniques - 2
 - [ ] Develop further hypothesis based on understanding of the series and create corresponding features - 4
 - [ ] Train alternate models - 2
 - [ ] Evaluate said models on test data and record metrics - 2
 - [ ] Compare and choose the best model for production deployment - 1

**Initiative**: Design and develop Web Application

**Epic**: Prepare for production deployment
 - [ ] Migrate model code to scripts - 2
 - [ ] Write unit tests and log - 2
 - [ ] Gather environment configuration requirements and library dependencies - 2
 - [ ] Create and review 'requirements.txt' - 1

**Epic**: Set up database and storage architecture
 - [ ] Identify data requirements for model deployment - 1
 - [ ] Design and create appropriate database structure - 2
 - [ ] Ensure databases are up to date and pipelines, if any, are in place - 4

**Epic**: Configure target environment
 - [ ] Identify current state of environment - 1
 - [ ] Determine target environment configuration - 1
 - [ ] Set target environment configuration - 1

**Epic**: Design front end of application
 - [ ] Conceptualize appropriate questions and their responses to enable user to create interesting characters - 4
 - [ ] Design layout of user interface - 2
 - [ ] Wireframe the UI to finalize design concepts - 2
 - [ ] Implement the finalized design - 4
 - [ ] Get feedback from sample of fans on experience - 2
 - [ ] *(icebox)* Brainstorm on additional results that can be displayed to add more context to the game and hence aid user engagement

**Epic**: Setting up application monitoring framework
 - [ ] Create model monitoring dashboards - 2
 - [ ] Establish model monitoring data pipelines - 4
 - [ ] Deploy and validate model performance requirements - 2
 - [ ] Establish application KPIs - 2
 - [ ] Establish and verify logging pipelines - 4
 - [ ] Validate application performance requirements - 2

**Epic**: Testing and Deployment
 - [ ] Release application to initial subset of users - 2
 - [ ] Identify problem areas (technical and conceptual) by entering end cases and examining app behaviour - 4
 - [ ] Rectify identified issues - 4
 - [ ] Deploy application - 1

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
eyJoaXN0b3J5IjpbNzQzNzEzOTE3LDIwNzU2NTk1NSwtMTYxMD
M5MjQxMCwtMTYxNzY1MzcxOCwyMTI5MDE3MjY2LDE1MjU1OTU1
MywtMjM5NTY2MTIzLDU4ODMwMzMzNSwtMTA4MjcxNDYzNSwxMD
I2MTM1NzcwLC0xMjYzMzQzODE0LC0xMzczNzE4MzUsLTEyODI4
OTgwMjUsNDk3Mjg3NjkyLC0yOTQwNDEwNzQsMTkxOTMxNzAwMl
19
-->