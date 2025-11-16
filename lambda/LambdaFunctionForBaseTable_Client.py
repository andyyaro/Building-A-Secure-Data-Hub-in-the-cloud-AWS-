import os, json, boto3
from dynamodb_encryption_sdk.encrypted.table import EncryptedTable
from dynamodb_encryption_sdk.material_providers.aws_kms import AwsKmsCryptographicMaterialsProvider

"""
Lambda function for the client application to retrieve encrypted client
information from a DynamoDB table that lives in a separate “data” account.

This function:
1. Assumes a role in the data account using the AWS Security Token Service (STS).
2. Uses the temporary credentials to read from a DynamoDB table.
3. Uses the DynamoDB Encryption Software Development Kit (SDK) with
   the AWS Key Management Service (KMS) to transparently decrypt the item.

Be sure to:
1. Set the following environment variables for the function:
   - DATA_ACCOUNT_ROLE_ARN
   - CLIENTS_TABLE_NAME
   - KMS_KEY_ALIAS
   - AWS_REGION (optional, default is us-east-1)
"""

DATA_ACCOUNT_ROLE_ARN = os.environ["DATA_ACCOUNT_ROLE_ARN"]
# Example: arn:aws:iam::123456789012:role/service-role/LambdaFunctionForBaseTable_Client-role-a1bcdefg 

CLIENTS_TABLE_NAME = os.environ.get("CLIENTS_TABLE_NAME", "ClientsBase")

KMS_KEY_ALIAS = os.environ.get("KMS_KEY_ALIAS", "alias/DemoKeyClientsBase")
# Example default: "alias/DemoKeyClientsBase".
# Remember to keep prefix "alias/" before the name of your KMS customer managed key.

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
# For Lambda, this is usually already set by the platform (for example, "us-east-1").


def assume_role_in_data_account():
    """
    Assume the cross-account role in the data account.

    Returns:
        dict: Temporary security credentials from AWS Security Token Service (STS),
              containing AccessKeyId, SecretAccessKey, and SessionToken.
    """
    sts_client = boto3.client("sts", region_name=AWS_REGION)

    response = sts_client.assume_role(
        RoleArn=DATA_ACCOUNT_ROLE_ARN,
        RoleSessionName="LambdaFunctionForBaseTable_Client",
    )

    print(f"Successfully assumed role {DATA_ACCOUNT_ROLE_ARN}.")
    return response["Credentials"]


def parse_client_id(event):
    """
    Extract the client identifier from the event.

    The mapping template in Amazon API Gateway builds an event shaped like:
        {
          "client_id": "...",
          "request_id": "...",
          ...
        }

    Args:
        event (dict): The event object passed to the Lambda function.

    Returns:
        str: The client id.
    """
    client_id = event["client_id"]
    print(f"Successfully retrieved client_id: {client_id} from request.")
    return client_id


def retrieve_client_info(client_id, temp_credentials):
    """
    Retrieve a client item from the encrypted DynamoDB table using the
    DynamoDB Encryption Software Development Kit (SDK).

    Args:
        client_id (str): The client identifier (partition key value).
        temp_credentials (dict): Temporary credentials returned by assume_role_in_data_account().

    Returns:
        dict: The decrypted item from the DynamoDB table.
    """
    # Create a new boto3.Session using the temporary credentials from the data account role.
    session = boto3.Session(
        aws_access_key_id=temp_credentials["AccessKeyId"],
        aws_secret_access_key=temp_credentials["SecretAccessKey"],
        aws_session_token=temp_credentials["SessionToken"],
        region_name=AWS_REGION,
    )

    # Standard DynamoDB Table handle using the cross-account session.
    table = session.resource("dynamodb").Table(CLIENTS_TABLE_NAME)

    # The AwsKmsCryptographicMaterialsProvider expects a botocore.session.Session,
    # which is exposed as `session._session` on the boto3.Session.
    aws_kms_cmp = AwsKmsCryptographicMaterialsProvider(
        key_id=KMS_KEY_ALIAS,
        botocore_session=session._session,
    )

    # Wrap the DynamoDB table with the Encryption SDK's EncryptedTable helper.
    encrypted_table = EncryptedTable(
        table=table,
        materials_provider=aws_kms_cmp,
    )

    # transparent decryption happens under the hood when we call get_item.
    response = encrypted_table.get_item(Key={"id": client_id})
    item = response["Item"]

    print(f"Successfully retrieved item from base table for id: {client_id}.")
    return item


def lambda_handler(event, context):
    """
    Lambda entry point.

    Args:
        event (dict): Event payload from Amazon API Gateway (already mapped by VTL).
        context (LambdaContext): Runtime information provided by AWS Lambda.

    Returns:
        dict: HTTP-style response with statusCode and JSON body.
    """
    print("Incoming event:") 
    print(event) #Priting the event helps with debugging.

    client_id = parse_client_id(event)
    temp_credentials = assume_role_in_data_account()
    item = retrieve_client_info(client_id, temp_credentials)

    print("Lambda context (for debugging):")
    print(context)

    return {
        "statusCode": 200,
        "body": json.dumps(item, indent=2),
    }


# ---------------------------------------------------------------------------
# Notes on boto3.Session vs botocore.session.Session and the Encryption SDK
# ---------------------------------------------------------------------------

# - boto3.Session is built on top of botocore.session.Session.
#   (boto3 wraps a botocore session internally as `session._session`.)
#
# - The AWS Key Management Service (KMS) itself does not care about sessions;
#   it only sees signed HTTP requests.
#
# - The DynamoDB Encryption Software Development Kit (SDK) class
#   AwsKmsCryptographicMaterialsProvider is written on top of botocore and its
#   function signature expects:
#
#       botocore_session: botocore.session.Session
#
# - Therefore:
#       boto3.Session != botocore.session.Session
#       boto3.Session wraps a botocore.session.Session as `session._session`.
#
# - If you do not pass a botocore.session.Session explicitly, the Encryption SDK
#   will fall back to the default session, which in a Lambda function is tied
#   to the Lambda execution role’s credentials.
#
# - In this pattern, we want to use the *assumed role* credentials from the
#   data account, so we explicitly pass `session._session` to
#   AwsKmsCryptographicMaterialsProvider.
#
# - Here is note on class definition for the AwsKmsCryptographicMaterialsProvider 
# - directly from the encryption sdk lib:
'''    class AwsKmsCryptographicMaterialsProvider(CryptographicMaterialsProvider):
    # pylint: disable=too-many-instance-attributes
    """Cryptographic materials provider for use with the AWS Key Management Service (KMS).

    .. note::

        This cryptographic materials provider makes one AWS KMS API call each time encryption
        or decryption materials are requested. This means that one request will be made for
        each item that you read or write.

    :param str key_id: ID of AWS KMS CMK to use
    :param botocore_session: botocore session object (optional)
    :type botocore_session: botocore.session.Session
    :param list grant_tokens: List of grant tokens to pass to KMS on CMK operations (optional)
    :param dict material_description: Material description to use as default state for this CMP (optional)
    :param dict regional_clients: Dictionary mapping AWS region names to pre-configured boto3
        KMS clients (optional)
    """ 
'''
