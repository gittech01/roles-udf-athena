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
    """
    Lambda handler para gerar URL pré-assinada para upload de arquivo.
    Espera um POST request com o seguinte formato no body:
    {
        "fileName": "nome-do-arquivo.ext",
        "contentType": "application/pdf",  # opcional
        "maxSize": 10485760  # opcional, tamanho máximo em bytes (10MB default)
    }
    """
    try:
        # Verifica se é um POST request
        if event.get('httpMethod') != 'POST':
            return {
                'statusCode': 405,
                'body': json.dumps({'error': 'Método não permitido. Use POST.'}),
                'headers': {'Content-Type': 'application/json'}
            }

        # Parse do body
        body = json.loads(event.get('body', '{}'))
        
        # Validações básicas
        if not body.get('fileName'):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'fileName é obrigatório'}),
                'headers': {'Content-Type': 'application/json'}
            }

        # Validações adicionais podem ser feitas aqui
        # Por exemplo, verificar contentType, maxSize, etc.
        
        object_name = body['fileName']
        bucket_name = "name-bucket"
        
        response = create_presigned_post(
            bucket_name, 
            object_name, 
            expiration=3600
        )
        
        return response

    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'JSON inválido no body'}),
            'headers': {'Content-Type': 'application/json'}
        }
    except Exception as e:
        logging.error(f"Erro inesperado: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Erro interno do servidor'}),
            'headers': {'Content-Type': 'application/json'}
        }


# Testes unitários
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
        'httpMethod': 'POST',
        'body': json.dumps({
            'fileName': 'teste.txt',
            'contentType': 'text/plain',
            'maxSize': 10485760
        })
    }   
    context = {}
    response = lambda_handler(event, context)
    assert response['statusCode'] == 200
    assert 'body' in response
    
    response_body = json.loads(response['body'])
    assert isinstance(response_body, dict)
    assert 'url' in response_body
    assert response_body['url'] is not None

@patch('boto3.client')
def test_lambda_handler_invalid_method(mock_boto3_client):
    event = {
        'httpMethod': 'GET',
        'body': json.dumps({
            'fileName': 'teste.txt'
        })
    }
    context = {}
    response = lambda_handler(event, context)
    assert response['statusCode'] == 405
    assert 'body' in response
    
    response_body = json.loads(response['body'])
    assert isinstance(response_body, dict)
    assert 'error' in response_body
    assert response_body['error'] == 'Método não permitido. Use POST.'

@patch('boto3.client')
def test_lambda_handler_missing_filename(mock_boto3_client):
    event = {
        'httpMethod': 'POST',
        'body': json.dumps({})
    }
    context = {}
    response = lambda_handler(event, context)
    assert response['statusCode'] == 400
    assert 'body' in response
    
    response_body = json.loads(response['body'])
    assert isinstance(response_body, dict)
    assert 'error' in response_body
    assert response_body['error'] == 'fileName é obrigatório'

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
    test_lambda_handler_invalid_method()
    test_lambda_handler_missing_filename()
    test_create_presigned_post()


