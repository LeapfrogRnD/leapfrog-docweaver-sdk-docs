import boto3
import json
import os
from botocore.exceptions import ClientError

ACCOUNT_ID = "654654390449"
REGION = "us-east-1"
ROLE_ARN = f"arn:aws:iam::{ACCOUNT_ID}:role/agentcore-gateway-role"

client = boto3.client("bedrock-agentcore-control", region_name=REGION)

with open("agentcore_tool_schema.json") as f:
    schema = json.load(f)

# Use existing gateway when provided; otherwise create one.
gateway_id = os.getenv("GATEWAY_ID", "docweaver-mcp-gateway-mupsmbrviv").strip()
if not gateway_id:
    response = client.create_gateway(
        name="docweaver-mcp-gateway",
        roleArn=ROLE_ARN,
        protocolType="MCP",
        authorizerType="NONE"
    )
    gateway_id = response["gatewayId"]

# Register Lambda target
try:
    client.create_gateway_target(
        gatewayIdentifier=gateway_id,
        name="docweaver-lambda",
        credentialProviderConfigurations=[
            {
                "credentialProviderType": "GATEWAY_IAM_ROLE",
            }
        ],
        targetConfiguration={
            "mcp": {
                "lambda": {
                    "lambdaArn": "arn:aws:lambda:us-east-1:654654390449:function:docweaver_mcp_server",
                    "toolSchema": {
                        "inlinePayload": schema
                    },
                }
            }
        },
    )
except ClientError as exc:
    if exc.response.get("Error", {}).get("Code") == "ConflictException":
        print("Gateway target 'docweaver-lambda' already exists. Keeping existing target.")
    else:
        raise

print(f"Gateway ID: {gateway_id}")