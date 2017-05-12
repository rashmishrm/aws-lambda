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
   update_json={}
   exprAttributeNames={}
   exprAttributeValues = {}
   item = input_json
   Key = {"menu_id":item.get('menu_id')}
   UpdateExpression = 'SET '
   needComma = False
   update_json["Key"] = Key
   i=1;
   print(len(item))
   for k,v in item.iteritems():
       if(k!="menu_id"):
           exprAttributeNames["#"+k]=k
           exprAttributeValues[":"+k+"v"]=v
           UpdateExpression  = UpdateExpression + "#"+k+" = :"+k+"v"
           if(i!=len(item)):
               UpdateExpression =  UpdateExpression+","
       i=i+1;
   update_json["ExpressionAttributeNames"]=exprAttributeNames
   update_json["ExpressionAttributeValues"]=exprAttributeValues
   update_json["TableName"]="Menu"
   update_json["UpdateExpression"]=UpdateExpression
   print (update_json)
   return update_json


def pizzaMenuHandler(event, context):
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
