import os
import config
import boto3
import botocore.exceptions
import logging.config

logging_config = 'config/logging/local.conf'

logging.config.fileConfig(logging_config)
logger = logging.getLogger('write_to_S3')

try:
    s3 = boto3.client('s3',
                    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"))
    try:
        s3.upload_file(config.RAW_DATA_FILE,
                       config.S3_BUCKET,
                       config.FILE_NAME)
        logger.info("{} written to S3 bucket {}".format(config.FILE_NAME, config.S3_BUCKET))

    except boto3.exceptions.S3UploadFailedError:
        # Checking for valid S3 bucket name
        logger.error("No such bucket! Please provide valid S3 bucket name")

    except FileNotFoundError:
        # Checking if file exists
        logger.error("File does not exist! Please provide valid file name")

except botocore.exceptions.PartialCredentialsError:
    # Checking for valid AWS credentials
    logger.error("Please provide valid AWS credentials")





