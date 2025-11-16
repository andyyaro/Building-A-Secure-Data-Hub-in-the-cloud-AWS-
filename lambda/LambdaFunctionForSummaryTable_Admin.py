import os, json, boto3

"""
Lambda function for the admin application to retrieve summary client
information from a DynamoDB table that lives in a separate "data" account. 

This function:
1. Assumes a role in the data account using the AWS Security Token Service (STS).
2. Uses the temporary credentials to scan the "summary" DynamoDB table.

Be sure to:
1. Set the following environment variables for the function:
   - DATA_ACCOUNT_ROLE_BLUE_ARN
   - CLIENTS_SUMMARY_TABLE_NAME
   - AWS_REGION (optional, default is us-east-1)
"""

DATA_ACCOUNT_ROLE_BLUE_ARN = os.environ["DATA_ACCOUNT_ROLE_BLUE_ARN"]
# Example: arn:aws:iam::123456789012:role/service-role/LambdaFunctionForSummaryTable_Client-role-a1bcdefg 

CLIENTS_SUMMARY_TABLE_NAME = os.environ.get("CLIENTS_SUMMARY_TABLE_NAME", "ClientsSummary")

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

def assume_role_in_data_account():
    """
    Assume the cross-account role in the data account.

    Returns:
        dict: Temporary security credentials from AWS Security Token Service (STS),
              containing AccessKeyId, SecretAccessKey, and SessionToken.
    """
    sts_client = boto3.client('sts')
    response = sts_client.assume_role(
        RoleArn=DATA_ACCOUNT_ROLE_BLUE_ARN,
        RoleSessionName="AssumeRoleInDataAccount"
    )
    print(f"Successfully assumed role {DATA_ACCOUNT_ROLE_BLUE_ARN}.")
    return response['Credentials']

def retrieve_client_info(temp_credentials):
    """ 
    Args:
        temp_credentials (dict): Temporary security credentials from AWS Security Token Service (STS),
              containing AccessKeyId, SecretAccessKey, and SessionToken.

    Returns:
        tuple: A tuple containing two elements:
            - list: A list of items retrieved from the DynamoDB table.
            - int: The count of items retrieved from the DynamoDB table.
    """
    session = boto3.Session(
        aws_access_key_id=temp_credentials['AccessKeyId'],
        aws_secret_access_key=temp_credentials['SecretAccessKey'],
        aws_session_token=temp_credentials['SessionToken'],
        region_name=AWS_REGION
    )
    table = session.resource('dynamodb').Table(CLIENTS_SUMMARY_TABLE_NAME)
    table_scan = table.scan(AttributesToGet=['id', 'firstName', 'lastName'], Limit=20)
    table_count = table_scan['Count']
    table_items = table_scan['Items']

    print(f"Successfully retrieved {table_count} items from {CLIENTS_SUMMARY_TABLE_NAME}.")

    return table_items, table_count

def lambda_handler(event, context):
    """ 
    Lambda function handler.

    Args:
        event (dict): The event data from the Lambda service.
        context (object): The context object from the Lambda service.

    Returns:
        dict: A dictionary containing the status code, count of items, and items retrieved from the DynamoDB table.
    """
    temp_credentials=assume_role_in_data_account()
    table_count=retrieve_client_info(temp_credentials)[1]
    table_items=retrieve_client_info(temp_credentials)[0]

    print("Lambda context (for debugging):")
    print(context)

    return {
        'statusCode': 200,
        'count': table_count,
        'items': json.dumps(table_items)
    }
