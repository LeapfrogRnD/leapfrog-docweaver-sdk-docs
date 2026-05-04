import boto3
import botocore.exceptions

def create_lambda_function():
    # Initialize the AWS Lambda client
    lambda_client = boto3.client('lambda', region_name='us-east-1')  # Change region as needed

    # Lambda function configuration
    function_name = "docweaver_mcp_server"
    role_arn = "arn:aws:iam::654654390449:role/lambda-execution-role"  # Replace with your role ARN
    image_uri = "654654390449.dkr.ecr.us-east-1.amazonaws.com/docweaver/mcp_server:latest"  # Replace with your ECR image URI
    tags = {
        "Name": "docweaver",
        "Deletable": "True",
        "Project": "docweaver",
        "Creator": "Adarsha Regmi"
    }

    try:
        # Create the Lambda function with ECR image
        response = lambda_client.create_function(
            FunctionName=function_name,
            Role=role_arn,
            Code={
                "ImageUri": image_uri
            },
            PackageType="Image",  # Specify that this is a container image
            Tags=tags,
            Timeout=30,  # Set timeout in seconds
            MemorySize=512,  # Set memory size in MB
            Publish=True  # Publish the function immediately
        )
        print("Lambda function created successfully!")
        print("Function ARN:", response['FunctionArn'])
    except botocore.exceptions.ClientError as e:
        print("AWS ClientError:", e.response['Error']['Message'])
    except botocore.exceptions.BotoCoreError as e:
        print("BotoCoreError:", str(e))
    except Exception as e:
        print("Unexpected error:", str(e))

# Call the function
create_lambda_function()