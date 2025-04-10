import json
import boto3
from botocore.exceptions import NoCredentialsError

def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    bucket_name = 'seu-bucket'
    file_key = event['queryStringParameters']['file_key']
    
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_key},
            ExpiresIn=60  # URL válida por 1 min
        )
        return {
            'statusCode': 200,
            'body': json.dumps({'url': url}),
            'headers': {'Content-Type': 'application/json'}
        }
    except NoCredentialsError:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Credenciais não encontradas'}),
            'headers': {'Content-Type': 'application/json'}
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
