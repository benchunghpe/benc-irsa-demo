import boto3
import requests
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch
from kubernetes import client, config

def get_iam_role_from_sa_annotation():
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    service_account_name = "default"
    namespace = "default"
    sa = v1.read_namespaced_service_account(service_account_name, namespace)
    annotations = sa.metadata.annotations
    return annotations.get("eks.amazonaws.com/role-arn", None)

def get_temp_credentials():
    sts_client = boto3.client('sts')
    assumed_role_object = sts_client.assume_role(
        RoleArn=get_iam_role_from_sa_annotation(),
        RoleSessionName='AssumedRoleSession'
    )
    credentials = assumed_role_object['Credentials']
    return credentials['AccessKeyId'], credentials['SecretAccessKey'], credentials['SessionToken']

def authenticate_to_opensearch():
    role_arn = get_iam_role_from_sa_annotation()
    if not role_arn:
        raise ValueError("Service account annotation for IAM role ARN not found")

    access_key, secret_key, session_token = get_temp_credentials()
    region = 'us-west-2'
    service = 'es'
    aws_auth = AWS4Auth(access_key, secret_key, region, service, session_token=session_token)
    opensearch_host = 'https://vpc-heliumops-globalsearch-6m6htouaujvnopm7gtwnpk6l4a.us-west-2.es.amazonaws.com'
    es = Elasticsearch(
        hosts=[{'host': opensearch_host, 'port': 443}],
        http_auth=aws_auth,
        use_ssl=True,
        verify_certs=True
    )
    return es

if __name__ == "__main__":
    es = authenticate_to_opensearch()
    print(es.info())
