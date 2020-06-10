import os
import boto3
import botocore.exceptions
import logging

logger = logging.getLogger(__name__)


def download_from_s3(RAW_DATA_DIR, FILE_NAMES=None, S3_BUCKET=None):
    """
    Downloads raw data from S3 bucket and stores in 'RAW_DATA_DIR' as defined in config/model_config.yaml

    Arguments:
        RAW_DATA_DIR: local file path to store raw data downloaded from S3
        FILE_NAMES: files to download from S3 bucket
        S3_BUCKET: S3 bucket to download from

    Returns:
        None
    """

    try:
        # set up S3 client using aws credentials as provided in config/credentials.env
        s3 = boto3.client('s3',
                          aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                          aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"))

        # downloads each of the files asked for from S3 bucket
        for file in FILE_NAMES:
            local_file = os.path.join(RAW_DATA_DIR, file)
            s3.download_file(S3_BUCKET, file, local_file)
            logger.info("{} downloaded from S3 bucket {}".format(local_file, S3_BUCKET))

    except botocore.exceptions.ClientError as e:
        # Checking for valid AWS credentials
        logger.error(e)
