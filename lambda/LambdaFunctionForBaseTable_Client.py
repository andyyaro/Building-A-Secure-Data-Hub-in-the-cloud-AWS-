import boto3, json
from dynamodb_encryption_sdk.encrypted.table import EncryptedTable
from dynamodb_encryption_sdk.material_providers.aws_kms import AwsKmsCryptographicMaterialsProvider

# Assuming the role in sdh-data.
def assuming_role_in_sdh_data():
  RoleArn = "arn:aws:iam::204687258468:role/service-role/LambdaFunctionForBaseTable_Client-role-t7abmruy"
  sts_client = boto3.client('sts')
  response = sts_client.assume_role(
    RoleArn = RoleArn,
    RoleSessionName = "LambdaFunctionForBaseTable_Client"
  )
  print(f"Successfully Assumed role {RoleArn}.")
  temp_credentials = response["Credentials"]
  return temp_credentials


# Parsing request for id. 
def parsing_for_id(event):
  claims = event["requestContext"]["authorizer"]["claims"]
  client_id = claims["custom:client_id"]
  print(f"Successfully retrieved Id: {client_id} from request.")
  return client_id

# Retrieving Client Item based on Id.
def retrieving_client_info(client_id, temp_credentials):
  session= boto3.Session(
    aws_access_key_id=temp_credentials['AccessKeyId'], 
    aws_secret_access_key=temp_credentials['SecretAccessKey'], 
    aws_session_token=temp_credentials['SessionToken'], 
    region_name='us-east-1', 
    aws_account_id='204687258468')
  table = session.resource('dynamodb').Table('ClientsBase')
  aws_kms_cmp = AwsKmsCryptographicMaterialsProvider('alias/DemoKeyClientsBase', session._session)
  encrypted_table = EncryptedTable(
      table=table,
      materials_provider=aws_kms_cmp
  )
  response = encrypted_table.get_item(Key={'id' : client_id})
  item = response['Item']
  print(f"Successfully retrieved Item from base table for id: {client_id}.")
  return item 
  
# Putting it all together and returning the client's info to the API.
def lambda_handler(event, context):
    item = retrieving_client_info(parsing_for_id(event), assuming_role_in_sdh_data())
    print(context)
    return {
        'statusCode': 200,
        'body': json.dumps(item, indent=2)
    }

# Clarifying Concepts for function retrieving_client_info:

# - boto3.Session is built on top of botocore.session.Session.
#   (boto3 wraps a botocore session internally as `session._session`.)

# - KMS (the AWS Key Management Service) doesn't care about sessions;
#   it just receives signed HTTP requests.

# - The DynamoDB Encryption SDK class AwsKmsCryptographicMaterialsProvider
#   is written on botocore and its function signature expects:
#       botocore_session: botocore.session.Session

# - boto3.Session != botocore.session.Session
# - boto3.Session wraps a botocore session as `session._session`

#if botocore.session.Session not passed, the function will use the default session
#the default session is that of the execution role attached to lambda, and contains those credentials 

# Here is note on class definition directly from the encryption sdk lib:
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
