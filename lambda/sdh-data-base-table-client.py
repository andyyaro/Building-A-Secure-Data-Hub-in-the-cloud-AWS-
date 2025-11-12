import boto3, json
from dynamodb_encryption_sdk.encrypted.table import EncryptedTable
from dynamodb_encryption_sdk.material_providers.aws_kms import AwsKmsCryptographicMaterialsProvider

#Assuming the role in sdh-data

sts_client = boto3.client('sts')
response = sts.assume_role(
  RoleArn = "MyRoleArn",
  RoleSessionName = "MySessionName"
)

# Parsing request for id 
""" TO DO """

temp_credentials = response["Credentials"]
print(f"Assumed role {assume_role_arn} and got temporary credentials.")

#Retrieving Client Item based on Id

table = boto3.resource('dynamodb').Table('ClientsBase')
aws_kms_cmp = AwsKmsCryptographicMaterialsProvider('alias/MyKmsAlias')
encrypted_table = EncryptedTable(
    table=table,
    materials_provider=aws_kms_cmp
)

response = encrypted_table.get_item('id' : '2a')
item = response['Item']
print(f"Retrieved Item from base table for id: {id}")

