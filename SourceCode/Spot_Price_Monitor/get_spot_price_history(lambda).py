import boto3

from datetime import datetime, timedelta

# 00. AWS Resource Initialize
dynamodb = boto3.resource('dynamodb')

# 01. AZ which has g2 instances
region_list = ['ap-northeast-1', 'ap-southeast-1', 'ap-southeast-2', 'eu-central-1', 'eu-west-1', 'us-east-1',
               'us-west-1', 'us-west-2']  # regions which have g2.instances


def lambda_handler(event, context):
    # 02. DynamoDB Instance -("g2-instance"->Where Spot Instances Price is stored)
    g2_spot_table = dynamodb.Table('g2-instance')

    # 03. Call API called "describe_spot_price_history" to fetch current spot price from each region
    for each_region in region_list:
        client = boto3.client('ec2', region_name=each_region)
        spot_price_dict = client.describe_spot_price_history(
            StartTime=datetime.now() - timedelta(minutes=1),
            EndTime=datetime.now(),
            InstanceTypes=[
                'g2.2xlarge'
            ],
            ProductDescriptions=[
                'Linux/UNIX (Amazon VPC)'
            ],
        )
        # 04. Save spot price from each region into DynamoDB Table
        for key, value in spot_price_dict.iteritems():
            if key == u'SpotPriceHistory':
                for i in value:
                    az = i[u'AvailabilityZone']
                    price = i[u'SpotPrice']
                    execute = g2_spot_table.put_item(
                        Item={
                            'az': az,
                            'price': price
                        }
                    )
