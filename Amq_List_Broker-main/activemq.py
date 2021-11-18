import  boto3
import requests
import json
import os
from botocore.exceptions import ClientError
import xml.etree.ElementTree as ET

client_Name = os.environ['client_Name']
send_to = os.environ['SendToEmail']
mq_user_Name = os.environ['broker_userName']
mq_password = os.environ['broker_Password']


def lambda_handler(event, context):
    try:
        clientName= os.environ['client_Name']
        get_request(clientName)
    except:
        print("An exception occurred while trying loop")
        
            
    



def get_secret(secret_name):
    print("in secret manager")
    region_name = "us-east-1"
     # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    print(client)
    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.
 
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            secret_json = json.loads(secret)
            return secret_json[secret_name]
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
             
    
def send_email():
    ses = boto3.client('ses')
    # Send Notification
    print(f'Send Notification to {send_to}')
    ses.send_email(
        Source="njaiswal@cogitocorp.com",
        Destination={
            'ToAddresses': send_to.split(","),
            },
        Message={
            'Subject': {
                'Data': CustomerNamereturn
                },
            'Body': {
                'Text': {
                    'Data': CustomerNamereturn +"has greate count please dequeue it"
                    }
                }
            }
    )
   
    


def get_request(broker_name):
    try:
        print("i am in get request to reterieve data")
        
        getPassword=get_secret(mq_password)
        print(getPassword)
        getUsername=get_secret(mq_user_Name)
        print(getUsername)
        url=geturl(broker_name) 
        print("this is url",url)
        req = requests.get(url,auth=(getUsername,getPassword ), verify=False)
        root = ET.fromstring(req.content)
        print(root)
        decoded_response = req.content.decode('utf-8')
        treeOne = ET.fromstring(decoded_response)
        global CustomerNamereturn

        
        for  child in treeOne.iter():
            CustomerName=(child.attrib.get('name'))
            MessageCount=(child.attrib.get('consumerCount'))
        
            if (CustomerName is not None):
               CustomerNamereturn=CustomerName
            if (MessageCount is not None):
               MessageCount = int(MessageCount)
               print(MessageCount,CustomerNamereturn)
               if(MessageCount >= 100):
                   send_email()     
                   return CustomerNamereturn,MessageCount
    except:
        print("exception is occured please check the broker details")
               
            
def geturl(broker_name):
    client = boto3.client('mq')
    response = client.list_brokers()
    
    for broker in response['BrokerSummaries']:
        if broker['BrokerName'] == broker_name:
            broker_id = broker['BrokerId']
            print(f'Broker Name = {broker_name}, Broker_id= {broker_id}')
            url1='https://'+broker_id+'-1.mq.us-east-1.amazonaws.com:8162/admin/xml/queues.jsp'
            url2= 'https://'+broker_id+'-2.mq.us-east-1.amazonaws.com:8162/admin/xml/queues.jsp'
            urls=[url1,url2]
            for i in range(len(urls)):
                print('my urls',(urls[i]))
                try:
                    request_response = requests.head(urls[i])
                    print(request_response)
                    status_code = request_response.status_code
                    print(status_code)
                    if  status_code == 401:
                        return urls[i]
                except:
                    print("check with another broker")
                        
