from __future__ import print_function

import boto3
import json

print('Loading function')

kms = boto3.client('kms', region_name='us-west-1')
def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }

def modifyRequest():
    tableName = "Menu"

def createUpdateJSON(input_json):

   x = json.dumps(input_json)
   item = json.loads(x)
   bod={}
   ExpressionAttributeNames={}
   ExpressionAttributeValues = {}
   item = input_json
   Key = {"menu_id":item.get('menu_id')}
   UpdateExpression = 'SET '
   needComma = False
   bod["Key"] = Key
   i=1;
   print(len(item))
   for k,v in item.iteritems():
       if(k!="menu_id"):
           ExpressionAttributeNames["#"+k]=k
           ExpressionAttributeValues[":"+k+"v"]=v
           UpdateExpression  = UpdateExpression + "#"+k+" = :"+k+"v"
           if(i!=len(item)):
               UpdateExpression =  UpdateExpression+","
       i=i+1;



   bod["ExpressionAttributeNames"]=ExpressionAttributeNames
   bod["ExpressionAttributeValues"]=ExpressionAttributeValues
   bod["TableName"]="Menu"
   #UpdateExpression = 'SET #SN = :SNV, #S = :SV, #SZ = :SZV, #P = :PV, #SH = :SHV'
   bod["UpdateExpression"]=UpdateExpression
   print (bod)
   return bod


def pizzaMenuHandler(event, context):
    '''Demonstrates a simple HTTP endpoint using API Gateway. You have full
    access to the request and response payload, including headers and
    status code.

    To scan a DynamoDB table, make a GET request with the TableName as a
    query string parameter. To put, update, or delete an item, make a POST,
    PUT, or DELETE request respectively, passing in the payload to the
    DynamoDB API as a JSON body.
    '''
    print("Received event: " + json.dumps(event, indent=2))
    tableName ="Menu"
    operation =event["operation"]
    operations = {
        'DELETE': lambda dynamo, x: dynamo.delete_item(**x),
        'GET': lambda dynamo, x: dynamo.get_item( **x),
        'POST': lambda dynamo, x: dynamo.put_item(**x),
        'PUT': lambda dynamo, x: dynamo.update_item(**createUpdateJSON(x)),
    }

    dynamodb = boto3.resource('dynamodb', region_name='us-west-1')

    table = dynamodb.Table(tableName)


    if operation in operations:
        response = operations[operation](table,event.get("payload"))
        meta_data = response['ResponseMetadata']




    if operation =='GET':
        print("Response " + json.dumps(response, indent=2))

        response =  response['Item']
    else:
        if meta_data['HTTPStatusCode'] ==200:
            response ="OK"
        else:
            response="ERROR"


    return response
