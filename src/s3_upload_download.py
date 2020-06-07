import os
import config
import boto3
import botocore.exceptions
import logging.config
import argparse

logging_config = 'config/logging/local.conf'

logging.config.fileConfig(logging_config)
logger = logging.getLogger('write_to_S3')


def upload_to_s3(s3_client, local_directory, s3_bucket):
    try:
        for root, dirs, files in os.walk(local_directory):
            for file in files:
                s3_client.upload_file(os.path.join(root, file), s3_bucket, file)
                logger.info("{} written to S3 bucket {}".format(file, s3_bucket))

    except boto3.exceptions.S3UploadFailedError:
        # Checking for valid S3 bucket name
        logger.error("No such bucket! Please provide valid S3 bucket name")


def download_from_s3(s3_client, file_names, s3_bucket, local_dir):
    try:
        for file in file_names:
            local_file = os.path.join(local_dir, file)
            s3_client.download_file(s3_bucket, file, local_file)
            logger.info("{} downloaded from S3 bucket {}".format(local_file, s3_bucket))

    except boto3.exceptions.S3DownloadFailedError:
        # Checking for valid S3 bucket name
        logger.error("No such bucket! Please provide valid S3 bucket name")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Upload or Download files from S3 bucket")
    parser.add_argument('step', help='Which step to run', choices=['upload', 'download'])

    args = parser.parse_args()

    try:
        s3 = boto3.client('s3',
                          aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                          aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"))

        if args.step == 'upload':
            upload_to_s3(s3, config.EXT_DATA_DIR, config.S3_BUCKET)
        elif args.step == 'download':
            download_from_s3(s3, config.FILE_NAMES, config.S3_BUCKET, config.RAW_DATA_DIR)

    except botocore.exceptions.PartialCredentialsError:
        # Checking for valid AWS credentials
        logger.error("Please provide valid AWS credentials")
