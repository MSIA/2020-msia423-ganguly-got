# MSiA 423 2020
## How long will you play the Game of Thrones?

 - Developer - Shreyashi Ganguly
 - Quality Assurance - Kristiyan Dimitrov

<!-- toc -->

- [Running Model Pipeline and Application](#Running-model-pipeline-and-application)
- [Project Charter](#project-charter)
- [Project Backlog](#project-backlog)
- [Directory structure](#directory-structure)

<!-- tocstop -->

## Running the data ingestion pipeline
### To run the model pipeline and application with default settings
**Things to ensure before proceeding**
 - [ ] You are on Northwestern VPN and Docker app is running
 - [ ] AWS credentials have been set as environment variables via  the following commands
  `export AWS_ACCESS_KEY_ID=<your key>`
  `export AWS_SECRET_ACCESS_KEY=<your secret key>`

> If user has been given access to my S3 bucket, we are good to go. If not, user must create and provide a valid S3 Bucket name in `config/model_config.yaml` both for `s3_upload` and `s3_download`. They would then have to execute the S3 data upload step as mentioned later in the document, *before* proceeding with the model pipeline

  
 - [ ] The *local* SQL Alchemy database connection string has been set up as,
 `export SQLALCHEMY_DATABASE_URI=`
> For example,
> relative path to local DB: sqlite:///data/got_simulator.db
> absolute path to local DB: sqlite://///Users/cmawer/Repos/2020-MSIA423-template-repository/data/tracks.db

**Reproduce Model Pipeline**

 - [ ] Build docker image
  `docker build -t got_make .`
 - [ ] Run model pipeline (download data from S3 bucket, clean, make features, train model and score offline base)
   `make pipeline`

**Run Application**

 - [ ] Store model serving data in `SQLALCHEMY_DATABASE_URI` defined above
  `make database`
 - [ ] Build docker image
  `docker build -f app/Dockerfile -t got_app .`
 - [ ] Run application
   `docker run -p 5000:5000 --name test got_app`

The terminal should now display  
`* Running on http://0.0.0.0:5000/` 
Click on the url to be directed to the application web page. Enjoy playing around!

**Run Unit Tests**

 - [ ] `make tests`
 *To stop the already running application docker container, execute `docker kill test` and `docker rm test` in a different terminal

### To execute the model pipeline step by step with configurable inputs
Docker image to be built same as above, i.e.,
`docker build -t got_make .`
If desired, all previous results and artifacts can be cleaned by running `make clean`
 - Upload raw data to S3 - **`make s3_upload`**
By default this pulls *all files* from `data/external`. To change this location use,  `make s3_upload S3_UPLOAD_PATH=<local file path>`
As mentioned before, if using your own S3 bucket, please mention the bucket name in `config/model_config.yaml`
`src/config.py`
 - Download raw data from S3 -  **`make s3_download`**
 Configurable path - download data location
 `make s3_download S3_DOWNLOAD_PATH=<local file path>`
 By default downloaded data saved in `data/raw_data`
 
 - Clean data - **`make clean_base`**
  Configurable paths - download data location, intermediate model data location
`make clean_base S3_DOWNLOAD_PATH=<local file path> MODEL_DATA=<local file path>`
By default downloaded data saved in `data/raw_data`
Creates`clean_base.csv` and saves in `data/model_data`

 - Create features and EDA plots - **`make features`**
   Configurable paths - download data location, intermediate model data location
`make features S3_DOWNLOAD_PATH=<local file path> MODEL_DATA=<local file path>`
By default downloaded data saved in `data/raw_data`
Creates`features.csv` and a folder `eda_plots` with bivariate feature plots in `data/model_data`
 
 - Train model - **`make model`**
    Configurable paths - intermediate model data location, model artifacts location
`make model MODEL_DATA=<local file path> MODEL_ARTIFACTS=<local file path>`
By default picks model data saved in `data/model_data`
This directive trains the classification model and stores artifacts like test performance metrics and model object in the folder `models`

- Score offline base for model serving - **`make score`**
Configurable paths - intermediate model data location, model artifacts location
`make score MODEL_DATA=<local file path> MODEL_ARTIFACTS=<local file path>`
By default creates offline score base and saves in `data/model_data` Picks exported model object from `models`

### To connect application to RDS database

 - Define the following environment variables

>  -	`export MYSQL_USER=<“master username” used to create the database server>` 
> 	- `export MYSQL_PASSWORD=<“master password” used to create the database server>` 
>  - `export MYSQL_HOST=<RDS instance endpoint from the console>` 
>  - `export MYSQL_PORT=<RDS instance port 3306>` 
>  - `export DATABASE_NAME=<name of the database created>`   

- Create and populate the RDS database with offline scored base -  `make database_rds`

**To only query from the RDS database *already created* by the developer, skip to **Step 6: Verifying database creation**

To create RDS database,
 - update the AWS RDS details in `.mysqlconfig` as follows, 

Enter `vi .mysqlconfig`

	- Set `MYSQL_USER` to the “master username” that you used to create the database server
	- Set `MYSQL_PASSWORD` to the “master password” that you used to create the database server
	- Set `MYSQL_HOST` to be the RDS instance endpoint from the console
	- Set `MYSQL_HOST` to be 3306
	- Set `DATABASE_NAME` to be the name of the database created

 - Set the environment variables in .mysqlconfig,

     `source .mysqlconfig`

### Step 3. Build docker image

    docker build -t got_image .

### Step 4. Write raw data to S3 bucket
Run the following command with your AWS credentials

    docker run -e AWS_ACCESS_KEY_ID=<aws_key> -e AWS_SECRET_ACCESS_KEY=<aws_secret_key> got_image src/write_to_s3.py

The file character-deaths.csv is now written to the S3 bucket!

### Step 5. Creating database for model serving
 -  Case 1: `CREATE_DB_LOCALLY=True` (creating local SQLite database)
```bash
docker run --mount type=bind,source="$(pwd)"/data,target=/app/data got_image src/createDB_RDS.py
```
 - Case 2: `CREATE_DB_LOCALLY=False` (creating AWS RDS database)
```bash
sh run_docker.sh
```
The database with the 'prediction' table has been created in SQLite/RDS with a dummy row.

***Note: If recreating the database add --t at the end of option1 and inside run_docker.sh file for option2, to avoid IntegrityErrors due to duplicate records*

### Step 6: Verifying database creation
If database is created in local SQLite, the same can be viewed/queried through applications like `DB Browser for SQLite`

If the database is created in RDS, it can be queried as follows,

 - Enter suitable `MYSQL_USER` and `MYSQL_PASSWORD` in `.mysqlconfig` (for users created for MSIA423 instructors and QA)
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
<!--stackedit_data:
eyJoaXN0b3J5IjpbLTg2Nzc4MzA4NiwtMzk0OTUwMTI4LC01ND
Q5NjkyNzMsLTE4OTc0MjU4NCw0ODU4NjQ3MjQsMTY0NTUxNTA3
MSwtNjA5MDk0Njc5LDExMjA5NjgxMTUsLTE4NDk2MjcxMTYsLT
ExNzkyNzIwMTEsLTE1NjE4Nzc3MiwtMTIxODkxNTk2LDU4ODMw
MzMzNSwtMTA4MjcxNDYzNSwxMDI2MTM1NzcwLC0xMjYzMzQzOD
E0LC0xMzczNzE4MzUsLTEyODI4OTgwMjUsNDk3Mjg3NjkyLC0y
OTQwNDEwNzRdfQ==
-->