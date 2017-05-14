import boto3
import base64

# 00. AWS Resource Initialize
dynamodb = boto3.resource('dynamodb')

# List of AMI-id in each region
ami_list = {'ap-northeast-1': 'ami-e1e6b486', 'ap-southeast-1': 'ami-81c476e2', 'ap-southeast-2': 'ami-05171a66',
            'eu-central-1': 'ami-340cdb5b', 'eu-west-1': 'ami-8c4278ea', 'us-east-1': 'ami-eab816fc',
            'us-west-1': 'ami-13386073', 'us-west-2': 'ami-6f31bf0f'}


# function get new region that has the lowest spot instance price
def get_region_with_lowest():
    g2_spot_table = dynamodb.Table('g2-instance')

    response = g2_spot_table.scan()

    temp_table = {}

    for key, values in response.iteritems():

        if key == "Items":

            for i in values:
                temp_table[str(i[u'az'])] = float(i[u'price'])

    new_az = min(temp_table, key=temp_table.get)  # return the key which has the lowest value

    # new_region = new_az[:-1]

    return new_az


# function to request new spot instance
def start_new_instance(user_data_param, new_az):
    new_region = new_az[:-1]

    client = boto3.client('ec2', region_name=new_region)

    user_data = 'checkpoint-file-path:mj-bucket-1/' + user_data_param + ',GitClone:git-clone-https://mjaysonnn:2####@github.com/mjaysonnn/code_for_deepspotcloud.git'

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
            'UserData': base64.b64encode(user_data.encode("ascii")).decode('ascii')
        }
    )
    return user_data


def lambda_handler(event, context):
    # 02. Request Params(user-data)
    ud = str(event.get('ud', None))

    # 03. get new region that has the lowest spot instance price
    new_az = get_region_with_lowest()

    sentence = "Starting new instance in " + new_az

    # 04. Call an API to request new spot instance
    user_data = start_new_instance(ud, new_az)

    print (sentence)
    print (user_data)
    return sentence





