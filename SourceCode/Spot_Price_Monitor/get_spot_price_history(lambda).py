import boto3
import pprint
from datetime import datetime, timedelta
import base64

dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('g2-instance')   #In DynamoDB there is a table named 'g2-instance'

region_list=['ap-northeast-1','ap-southeast-1','ap-southeast-2','eu-central-1','eu-west-1','us-east-1','us-west-1','us-west-2'] #regions which have g2.instances

def lambda_handler(event, context):
   

    for each_region in region_list:
        client=boto3.client('ec2',region_name=each_region)
        response = client.describe_spot_price_history(
        StartTime=datetime.now()-timedelta(minutes=1), 
        EndTime=datetime.now(),
        InstanceTypes=[
        'g2.2xlarge'
        ],
        ProductDescriptions=[
        'Linux/UNIX (Amazon VPC)'
        ],
    )
        for key, value in response.iteritems():    
            if key==u'SpotPriceHistory':          
                for i in value:                   
                    az=i[u'AvailabilityZone']     
                    price=i[u'SpotPrice']
                    response = table.put_item(
                    Item={
                    'az': az ,
                    'price':price
                    }
                    )   
                        
    
        
    
    
    