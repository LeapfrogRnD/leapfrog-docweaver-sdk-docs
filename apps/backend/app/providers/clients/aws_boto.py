"""AWS Bedrock client provider."""

import boto3
from botocore.client import BaseClient


def get_boto_client(
    service_name: str = "bedrock-runtime", region_name: str = "us-east-1"
) -> BaseClient:
    """
    Returns an AWS Bedrock client initialized with credentials from config.

    Returns:
        boto3 Bedrock runtime client
    """
    return boto3.client(
        service_name=service_name,
        region_name=region_name,
    )
