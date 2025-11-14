import boto3, json
from dynamodb_encryption_sdk.encrypted.table import EncryptedTable
from dynamodb_encryption_sdk.material_providers.aws_kms import AwsKmsCryptographicMaterialsProvider

# Assuming the role in sdh-data.
sts_client = boto3.client('sts')
response = sts_client.assume_role(
  RoleArn = "MyRoleArn",
  RoleSessionName = "MySessionName"
)
temp_credentials = response["Credentials"]
print(f"Successfully Assumed role {assume_role_arn}.")

# Parsing request for id. 
def parsing_for_id(event):
  claims = event["requestContext"]["authorizer"]["claims"]
  client_id = claims["custom:client_id"]
  print(f"Successfully retrieved Id: {client_id} from request.")
  return client_id

# Retrieving Client Item based on Id.
def retrieving_client_info(client_id):
  table = boto3.resource('dynamodb').Table('ClientsBaseTable')
  aws_kms_cmp = AwsKmsCryptographicMaterialsProvider('alias/MyKmsAlias')
  encrypted_table = EncryptedTable(
      table=table,
      materials_provider=aws_kms_cmp
  )
  response = encrypted_table.get_item('id' : client_id)
  item = response['Item']
  print(f"Successfully retrieved Item from base table for id: {client_id}")
  return item 
  
# Putting it all together and returning the client's info to the API.
def lambda_handler(event, context):
    item = retrieving_client_info(parsing_for_id(event))
    print(context)
    return {
        'statusCode': 200,
        'body': json.dumps(item)
    }

