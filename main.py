import boto3
import requests
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection
from kubernetes import client, config

def get_temp_credentials():
    sts_client = boto3.client('sts')
    assumed_role_object = sts_client.assume_role(
        RoleArn='arn:aws:iam::740665670670:role/heliumops-globalsearch-role-oidc',
        RoleSessionName='AssumedRoleSession'
    )
    credentials = assumed_role_object['Credentials']
    return credentials['AccessKeyId'], credentials['SecretAccessKey'], credentials['SessionToken']

def authenticate_to_opensearch():
    access_key, secret_key, session_token = get_temp_credentials()
    region = 'us-west-2'
    service = 'es'
    aws_auth = AWS4Auth(access_key, secret_key, region, service, session_token=session_token)
    opensearch_host = 'https://vpc-heliumops-globalsearch-6m6htouaujvnopm7gtwnpk6l4a.us-west-2.es.amazonaws.com'
    es = Elasticsearch(
        hosts=opensearch_host,
        http_auth=aws_auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    return es

if __name__ == "__main__":
    es = authenticate_to_opensearch()
    print(es.info())
