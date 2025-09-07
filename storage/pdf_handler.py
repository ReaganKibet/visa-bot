# storage/pdf_handler.py
import boto3
from botocore.exceptions import BotoCoreError
import logging

S3_BUCKET = "vfs-appointment-pdfs"
REGION = "eu-west-1"

def upload_pdf_to_s3(local_path: str, key: str) -> str:
    s3 = boto3.client('s3', region_name=REGION)
    try:
        s3.upload_file(local_path, S3_BUCKET, key, ExtraArgs={'ContentType': 'application/pdf'})
        url = f"https://{S3_BUCKET}.s3.{REGION}.amazonaws.com/{key}"
        logging.info(f"PDF uploaded: {url}")
        return url
    except BotoCoreError as e:
        logging.error(f"S3 upload failed: {e}")
        raise