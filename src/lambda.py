import json
import base64
import boto3
import os

s3_client = boto3.client('s3')
dynamodb = boto3.client('dynamodb')
BUCKET_NAME = os.getenv('BUCKET_NAME')
TABLE_NAME = os.getenv('TABLE')


def handler(event, context):

    if event.get('Records'):
        event_time = event['Records'][0]['eventTime']
        s3_details = event['Records'][0]['s3']
        key = s3_details['object']['key']

        item = {
            'name': {'S': key.split('.')[0]},  # String primary key
            'extension': {'S': key.split('.')[-1]},  # String sort key (if your table uses one)
            'time': {'S': event_time}
        }
        response = dynamodb.put_item(
            TableName=TABLE_NAME,
            Item=item
        )

        print("PutItem succeeded:", response)
        return response
    elif event.get('resource'):
        if event['resource'] == '/fetch':
            name = event['headers']['name']
            file_type = event['headers'].get('type')
            search_key = {'name': {'S': name}}

            if file_type:
                search_key['extension'] = {'S': file_type}

            response = dynamodb.get_item(
                TableName=TABLE_NAME,
                Key=search_key
            )

            if 'Item' in response:
                print(response)
                # The item is returned as a dictionary with data types (S, N, etc.)
                final_response = {
                    'statusCode': 200,
                    'body': json.dumps(response['Item'])
                }
            else:
                print("Item not found.")
                final_response = {
                    'statusCode': 403,
                    'body': "Not Found"
                }
            return final_response






