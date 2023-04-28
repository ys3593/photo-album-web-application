import json
from datetime import datetime
from requests_aws4auth import AWS4Auth
import requests
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection

# retrieves the source S3 bucket name and the key name of the uploaded object from the event parameter that it receives
# uses the Amazon S3 getObject API to retrieve the content type of the object
s3 = boto3.client('s3')


def lambda_handler(event, context):
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    labels = get_labels(bucket, key)
    response = store(key, bucket, labels)


def get_labels(bucket, key):
    labels = []

    rekognition = boto3.client('rekognition')
    response = rekognition.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': key}}, MaxLabels=10)
    for label in response["Labels"]:
        labels.append(label["Name"].lower())

    try:
        metadata = s3.head_object(Bucket=bucket, Key=key)
        if 'x-amz-meta-customlabels' in metadata['ResponseMetadata']['HTTPHeaders']:
            customlabels = metadata['ResponseMetadata']['HTTPHeaders']['x-amz-meta-customlabels']
            print(f"customlabels is {customlabels}")

            if customlabels:
                for label in customlabels.split(','):
                    labels.append(label.strip().lower())
    except Exception as e:
        print(e)

    return labels


def store(key, bucket, labels):
    photo = {
        'objectKey': key,
        'bucket': bucket,
        'createdTimeStamp': datetime.now().strftime("%y-%m-%d %H:%M:%S"),
        'labels': labels
    }
    # json_photo = json.dumps(photo)

    cred = boto3.Session().get_credentials()
    awsauth = AWS4Auth(cred.access_key, cred.secret_key, 'us-east-1', 'es', session_token=cred.token)
    client = OpenSearch(
        hosts=[{'host': "search-photos-xwi7s7hjphuxr4s2kirse6vf2u.us-east-1.es.amazonaws.com", 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

    index_name = 'photos'
    response = client.index(
        index=index_name,
        body=photo,
        id=key,
        refresh=True
    )

    print('\nAdding document:')
    print(response)
    return response