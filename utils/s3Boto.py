import boto3
from decouple import config
from django.conf import settings


AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_REGION = settings.AWS_REGION
AWS_BUCKET_NAME = settings.AWS_BUCKET_NAME


s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )


def save_file_to_s3(local_path, s3_key):
    s3.upload_file(local_path, AWS_BUCKET_NAME, s3_key)


def download_file_from_s3(local_path, s3_key):
    s3.download_file(AWS_BUCKET_NAME, s3_key, local_path)
