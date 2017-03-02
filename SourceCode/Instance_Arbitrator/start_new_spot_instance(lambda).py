import boto3
# import pprint
import base64

# import pycurl
# import cStringIO
# import json

dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('g2-instance')

ami_list = {'ap-northeast-1': 'ami-####', 'ap-southeast-1': 'ami-###', 'ap-southeast-2': 'ami-###',
            'eu-central-1': 'ami-####', 'eu-west-1': 'ami-###', 'us-east-1': 'ami-###',
            'us-west-1': 'ami-###', 'us-west-2': 'ami-###'}


def lambda_handler(event, context):
    ud = '{}'.format(event['ud'])

    response = table.scan()

    a_table = {}

    for key, values in response.iteritems():

        if key == "Items":

            for i in values:
                a_table[str(i[u'az'])] = float(i[u'price'])

    new_az = min(a_table, key=a_table.get)  # return the key which has the lowest value

    new_region = new_az[:-1]

    sentence = "Starting new instance in " + new_az



    client = boto3.client('ec2', region_name=new_region)

    data = 'checkpoint-file-path:mj-bucket-1/' + ud

    response = client.request_spot_instances(

        SpotPrice='0.65',
        InstanceCount=1,

        Type='one-time',
        LaunchSpecification={

            'ImageId': ami_list[new_region],
            'KeyName': 'macbook-mj',
            'InstanceType': 'g2.2xlarge',
            'SecurityGroups': ['mj-security'],

            'Placement': {
                'AvailabilityZone': new_az
            },
            'UserData': base64.b64encode(data.encode("ascii")).decode('ascii')
        }
    )
    return sentence





