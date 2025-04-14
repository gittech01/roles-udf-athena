import json

import logging
import boto3
from unittest.mock import patch, MagicMock
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

# crie teste unitario para a função lambda_handler
@patch('boto3.client')
def test_lambda_handler(mock_boto3_client):
    # Mock the S3 client response
    mock_s3 = MagicMock()
    mock_boto3_client.return_value = mock_s3
    mock_s3.generate_presigned_post.return_value = {
        'url': 'https://test-url.com',
        'fields': {'key': 'value'}
    }

    event = {
        'queryStringParameters': {
            'file_name': 'teste.txt'
        }
    }   
    context = {}
    response = lambda_handler(event, context)
    assert response['statusCode'] == 200
    assert 'body' in response
    
    # Parse the nested response structure
    response_body = json.loads(response['body'])
    assert isinstance(response_body, dict)

# crie teste unitario para a função create_presigned_post
@patch('boto3.client')
def test_create_presigned_post(mock_boto3_client):
    # Mock the S3 client response
    mock_s3 = MagicMock()
    mock_boto3_client.return_value = mock_s3
    mock_s3.generate_presigned_post.return_value = {
        'url': 'https://test-url.com',
        'fields': {'key': 'value'}
    }

    bucket_name = "name-bucket"
    object_name = "teste.txt"
    expiration = 3600
    response = create_presigned_post(bucket_name, object_name, expiration)
    assert response['statusCode'] == 200
    assert json.loads(response['body'])['url'] is not None

if __name__ == '__main__':
    test_lambda_handler()
    test_create_presigned_post()


