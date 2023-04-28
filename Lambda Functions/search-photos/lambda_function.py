import json

import boto3
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection
import uuid
import inflect
import requests

# Given a search query “q”, disambiguate the query using the Amazon Lex bot.
# If the Lex disambiguation request yields any keywords (K1, ..., Kn),
# search the “photos” OpenSearch index for results, and return them accordingly
# Otherwise, return an empty array of results
client = boto3.client('lexv2-runtime')


def lambda_handler(event, context):
    print(f"The event message is : {event}")
    keywords = []
    # q = "show me cats and dogs"
    q = event["queryStringParameters"]["q"]

    # Initiate conversation with Lex
    response = client.recognize_text(
        botId='RMKYPOKXTS',  # MODIFY HERE
        botAliasId='OK8TROIYXN',  # MODIFY HERE
        localeId='en_US',
        sessionId=str(uuid.uuid4()),
        text=q)

    print(f"The response message is : {response}")
    slots = response["sessionState"]["intent"]["slots"]
    print(f"The slot is : {slots}")

    if slots:
        p = inflect.engine()
        keyword = slots["query_term1"]["value"]["interpretedValue"].lower()
        singular = p.singular_noun(keyword)
        if singular:
            keywords.append(singular)
        else:
            keywords.append(keyword)

        if slots["query_term2"]:
            keyword = slots["query_term2"]["value"]["interpretedValue"].lower()
            singular = p.singular_noun(keyword)
            if singular:
                keywords.append(singular)
            else:
                keywords.append(keyword)

        results = search(keywords)

        print(f"The keywords message is : {keywords}")
        print(f"The results message is : {results}")
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*',
            },
            'body': json.dumps(results)
        }
    else:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*',
            },
            'body': json.dumps([])
        }



def search(keywords):
    paths = []
    cred = boto3.Session().get_credentials()
    awsauth = AWS4Auth(cred.access_key, cred.secret_key, 'us-east-1', 'es', session_token=cred.token)

    for k in keywords:
        url = 'https://search-photos-xwi7s7hjphuxr4s2kirse6vf2u.us-east-1.es.amazonaws.com/photos' + '/_search?q=' + k
        response = requests.get(url, auth=awsauth).json()
        if 'hits' in response:
            for r in response['hits']['hits']:
                path = "https://" + r['_source']['bucket'] + ".s3.amazonaws.com/" + r["_source"]["objectKey"]
                if path not in paths:
                    paths.append(path)

    return paths

