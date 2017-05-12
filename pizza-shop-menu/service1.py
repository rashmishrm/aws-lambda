from __future__ import print_function

import boto3
import json
import datetime

from time import gmtime, strftime

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


def identifyOrderStep(order,menu):
    sequence = menu["sequence"];
    step ="";
    step ="done"
    if "orders" in order:

        orderM = order ["orders"]

        for seq in sequence:
            print("here"+seq)
            if( seq not in   orderM):
                print("here"+seq)

                step =seq;
                break;

    return step;


def getOptionsString(step,menu):
    options = menu[step]
    i =1;
    optionStr=""
    for option in options:
        optionN = str(i)+")"+option
        optionStr = optionStr+" "+optionN
        if i!=len(options):
            optionStr =optionStr+","
        i=i+1;
    return optionStr;

def getPrice(step,option,menu):
    pprice=None
    if(step=="size"):
        price = menu["price"]
        sizes = menu["size"]
        pprice=None
        pprice = "$"+price[int(option)-1]

    return pprice

def getResponseString(order,menu):
    step = identifyOrderStep(order,menu)
    pprice=""
    #getting options for step
    if(step != "done"):
        options = getOptionsString(step,menu)
    else:
        price =menu["price"]
        sizes = menu["size"]
        if("orders" in order):
            orders = order["orders"]
            pprice = orders["costs"]



    initialStr=""
    customer_name =order["customer_name"]
    if(step =="selection"):
        initialStr="Hi "+customer_name+", please choose one of these selection:"
        response = initialStr +" "+ options;
    elif(step=="size"):
        initialStr ="Which size do you want?"
        response = initialStr +" "+ options;
    elif(step == "done"):
        response ="Your order costs "+pprice+". We will email you when the order is ready. Thank you!"
    return response;



def getOptionToStore(order,menu,input_option):
    updatejson = None
    step = identifyOrderStep(order,menu)
    pprice =getPrice(step,input_option,menu)
    if(step != "done"):
        order_id =order["order_id"]
        options = menu[step]

        toAdd = options[int(input_option)-1]

        updatejson= {}
        updatejson["TableName"] ="order"
        key ={}
        key["order_id"]=order_id
        updatejson["Key"] =key
        attributeNames = {}
        attributeNames["#SV"]=step
        updateExpr = "set orders.#SV= :V"
        attributeValues = {}
        attributeValues[":V"]=toAdd

        if(pprice is not None):
            updateExpr =updateExpr+ ", orders.#Costs = :C"
            print("price **** "+pprice)

            attributeNames["#Costs"]="costs"
            attributeValues[":C"]=pprice


        updatejson["ReturnValues"] ="NONE"
        updatejson["UpdateExpression"]=updateExpr
        updatejson["ExpressionAttributeValues"]=attributeValues
        updatejson["ExpressionAttributeNames"]=attributeNames

    return updatejson;






def orderHandler(event, context):
    '''Demonstrates a simple HTTP endpoint using API Gateway. You have full
    access to the request and response payload, including headers and
    status code.

    To scan a DynamoDB table, make a GET request with the TableName as a
    query string parameter. To put, update, or delete an item, make a POST,
    PUT, or DELETE request respectively, passing in the payload to the
    DynamoDB API as a JSON body.
    '''
    print("Received event: " + json.dumps(event, indent=2))
    tableName ="order"
    operation =event["operation"]
    operations = {
        'DELETE': lambda dynamo, x: dynamo.delete_item(**x),
        'GET': lambda dynamo, x: dynamo.get_item( **x),
        'POST': lambda dynamo, x: dynamo.put_item(**x),
        'PUT': lambda dynamo, x: dynamo.update_item(**x),
    }

    dynamodb = boto3.resource('dynamodb', region_name='us-west-1')
    table = dynamodb.Table(tableName)
    payload =event.get("payload");

    if (operation=="PUT"):
        order_id = payload["order_id"]
        input_option = payload["input"]
        orderPayload = {"Key":{ "order_id":order_id}}
        oResponse = operations["GET"](table,orderPayload)
        orderR =  oResponse['Item']

        menu_id =orderR["menu_id"]
        print ("Menu_ID " +menu_id)
        menuPayload = {"Key":{ "menu_id":menu_id}}
        menu = dynamodb.Table("Menu")
        mResponse = operations["GET"](menu,menuPayload)
        print("Received event: " + json.dumps(mResponse, indent=2))
        menuR =  mResponse['Item']

        store= getOptionToStore(orderR,menuR,input_option)
        print("Updating this: " + json.dumps(store, indent=2))
        if store !=None:
            response = operations[operation](table,store)

    elif(operation=="POST"):
        payload = event.get('payload')
        item = payload["Item"]
        orders ={}

        cTime =strftime("%m-%d-%y@%H:%M:%S", gmtime())
        orders["order_time"] =cTime
        orders["costs"] ="0"
        item["orders"]= orders
        item["order_status"] ="Processing"

        response = operations[operation](table,event.get('payload'))


    if operation in ("GET","DELETE"):
        response = operations[operation](table,event.get('payload'))
        meta_data = response['ResponseMetadata']

    if (operation in ("PUT","POST")):
        if operation == "PUT":

            order_id = payload["order_id"]
            input_option = payload["input"]
        else:
            item = payload["Item"]
            order_id = item["order_id"]
            input_option = "Initial"

        orderPayload = {"Key":{ "order_id":order_id}}
        oResponse = operations["GET"](table,orderPayload)
        orderR =  oResponse['Item']
        print("Updated " + json.dumps(orderR, indent=2))

        menu_id =orderR["menu_id"]
        menuPayload = {"Key":{ "menu_id":menu_id}}
        menu = dynamodb.Table("Menu")
        mResponse = operations["GET"](menu,menuPayload)
        menuR =  mResponse['Item']

        response= getResponseString(orderR,menuR)

    elif operation =='GET':
        response =  response['Item']
    else:
        if meta_data['HTTPStatusCode'] ==200:
            response ="OK"
        else:
            response="ERROR"


    return response
