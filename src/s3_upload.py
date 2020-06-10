import os
import boto3
import botocore.exceptions
import logging

logger = logging.getLogger(__name__)


def upload_to_s3(EXT_DATA_DIR, S3_BUCKET=None):
    """
    Uploads files to S3 bucket

    Arguments:
        EXT_DATA_DIR: local file directory holding raw data to be uploaded to S3
        S3_BUCKET: the name of S3 bucket to upload to

    Returns:
        None
    """
    try:
        # creates S3 client using AWS credentials provided in config/credentials.env
        s3 = boto3.client('s3',
                          aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                          aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"))
        try:
            # uploads all files in provided local directory to S3 bucket
            for root, dirs, files in os.walk(EXT_DATA_DIR):
                for file in files:
                    s3.upload_file(os.path.join(root, file), S3_BUCKET, file)
                    logger.info("{} written to S3 bucket {}".format(file, S3_BUCKET))

        except boto3.exceptions.S3UploadFailedError:
            # Checking for valid S3 bucket name
            logger.error("No such bucket! Please provide valid S3 bucket name")

        except FileNotFoundError:
            # Checking if file exists
            logger.error("File does not exist! Please provide valid file name")

    except botocore.exceptions.PartialCredentialsError:
        # Checking for valid AWS credentials
        logger.error("Please provide valid AWS credentials")
