import boto3
import os
import logging

def upload_content_to_s3(space_id, node_id, content_html):
    bucket = os.environ.get('CONTENT_BUCKET_NAME')
    key = f'nodes/{space_id}/{node_id}/content.html'
    s3 = boto3.client('s3')
    try:
        s3.put_object(Bucket=bucket, Key=key, Body=content_html, ContentType='text/html')
        return key
    except Exception as e:
        logging.error(f"Failed to upload content to S3: {e}")
        raise
