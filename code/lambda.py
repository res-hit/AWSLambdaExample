import json
import boto3
import os
from custom_encoder import CustomEncoder
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# get table instance which provides calls to dynamoDB service
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('TABLE_NAME'))  # environ var defined in sam template

get_method = 'GET'
put_method = 'PUT'

# in this example path not needed, we have 2 distinct method for different resources
vehicles_path = '/MyVehicleStore/vehicles'
vehicle_idPath = '/MyVehicleStore/vehicles/{vin}'


def lambda_handler(event, context):
    print(event)
    http_method = event['httpMethod']

    if http_method == get_method:
        response = get_item(event['pathParameters']['vin'])

    if http_method == put_method:
        body = event['body']
        body_dict = json.loads(body)
        response = put_item(body_dict['vehicle'])

    return response


def get_item(vin):
    print(vin)

    try:
        response = table.get_item(
            Key={

                'vin': vin

            }
        )

        # Item seems a field returned from get_item() contained in response dict
        if 'Item' in response:
            return send_response(200, response['Item'])
        else:
            return send_response(404, 'Message: vin: % not found' % vin)

    except:
        logger.exception('error handling.....')


def put_item(vehicle):
    try:
        table.put_item(Item=vehicle)
        response_body = {

            'Operation': 'PUT',
            'Message': 'Success',
            'Item': vehicle

        }

        return send_response(200, response_body)
    except:
        logger.exception('error handling code...')


def send_response(statusCode, body=None):
    response = {

        'statusCode': statusCode,
        'headers': {
            'Content-type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }

    }
    if body is not None:  # user passes a custom object
        response['body'] = json.dumps(body, cls=CustomEncoder)  # objects returned by dynamoDB are not supported by json

    print(response)

    return response
