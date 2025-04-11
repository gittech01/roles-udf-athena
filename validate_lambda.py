import boto3
import json
import os
import base64
import io
import pandas as pd

s3 = boto3.client('s3')
BUCKET = os.environ.get('UploadBucket')

ALLOWED_HEADERS = ['id', 'name', 'email']

def handler(event, context):
    try:
        body = json.loads(event['body'])
        file_name = body.get('fileName')
        file_content_b64 = body.get('fileContent')

        if not file_name or not file_content_b64:
            return _response(400, 'Missing fileName or fileContent.')

        decoded = base64.b64decode(file_content_b64)
        file_stream = io.BytesIO(decoded)

        if file_name.endswith('.csv'):
            df = pd.read_csv(file_stream)
        elif file_name.endswith('.xlsx'):
            df = pd.read_excel(file_stream)
        elif file_name.endswith('.txt'):
            text = decoded.decode()
            if "FORBIDDEN" in text:
                return _response(422, 'Invalid content in .txt file.')
            # Assume ok
        else:
            return _response(400, 'Unsupported file type.')

        # Validate CSV/XLSX columns
        if file_name.endswith(('.csv', '.xlsx')):
            if list(df.columns) != ALLOWED_HEADERS:
                return _response(422, f'Invalid headers: {list(df.columns)}. Expected: {ALLOWED_HEADERS}')

        # Generate presigned URL
        presigned_url = s3.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': BUCKET,
                'Key': file_name,
                'ContentType': _get_content_type(file_name)
            },
            ExpiresIn=300
        )

        return _response(200, {'uploadURL': presigned_url})

    except Exception as e:
        return _response(500, f'Error: {str(e)}')

def _get_content_type(file_name):
    if file_name.endswith('.csv'):
        return 'text/csv'
    if file_name.endswith('.xlsx'):
        return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    if file_name.endswith('.txt'):
        return 'text/plain'
    return 'application/octet-stream'

def _response(status, body):
    return {
        'statusCode': status,
        'body': json.dumps(body),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }



import json

import logging
import boto3
from botocore.exceptions import (
    ClientError, NoCredentialsError
)

def create_presigned_post(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL S3 POST request to upload a file

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Dictionary with the following keys:
        url: URL to post to
        fields: Dictionary of form fields and values to submit with the POST
    :return: None if error.
    """

    s3_client = boto3.client('s3')
    try:
        url_presigned = s3_client.generate_presigned_post(
            bucket_name,
            object_name,
            ExpiresIn=expiration
        )
    except ClientError as e:
        logging.error(e)
        return None
    except NoCredentialsError:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Credenciais não encontradas'}),
            'headers': {'Content-Type': 'application/json'}
        }

    return {
            'statusCode': 200,
            'body': json.dumps({'url': url_presigned}),
            'headers': {'Content-Type': 'application/json'}
        }
    
    
def lambda_handler(event, context):
    
    object_name = event['queryStringParameters']['file_name']
    bucket_name = "name-bucket"
    
    response = create_presigned_post(
        bucket_name, 
        object_name, 
        expiration=3600
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
