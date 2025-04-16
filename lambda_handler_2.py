// ... existing code ...

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
            'maxSize': 1024
        })
    }
    context = {}
    response = lambda_handler(event, context)
    assert response['statusCode'] == 200
    assert 'body' in response
    
    # Parse the nested response structure
    response_body = json.loads(response['body'])
    assert isinstance(response_body, dict)
    assert 'url' in response_body
    assert response_body['url'] is not None

@patch('boto3.client')
def test_lambda_handler_missing_parameters(mock_boto3_client):
    # Test case for missing fileName
    event = {
        'httpMethod': 'POST',
        'body': json.dumps({
            'contentType': 'text/plain',
            'maxSize': 1024
        })
    }
    context = {}
    response = lambda_handler(event, context)
    assert response['statusCode'] == 400
    assert 'body' in response
    
    response_body = json.loads(response['body'])
    assert isinstance(response_body, dict)
    assert 'error' in response_body
    assert response_body['error'] == 'fileName parameter is required'

@patch('boto3.client')
def test_lambda_handler_invalid_method(mock_boto3_client):
    # Test case for invalid method (GET)
    event = {
        'httpMethod': 'GET',
        'body': json.dumps({
            'fileName': 'teste.txt',
            'contentType': 'text/plain',
            'maxSize': 1024
        })
    }
    context = {}
    response = lambda_handler(event, context)
    assert response['statusCode'] == 400
    assert 'body' in response
    
    response_body = json.loads(response['body'])
    assert isinstance(response_body, dict)
    assert 'error' in response_body
    assert response_body['error'] == 'Invalid method'

// ... existing code ...