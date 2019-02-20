import boto3
import base64

# 00. AWS Resource Initialize
dynamodb = boto3.resource('dynamodb')

#  List of AMI-id in each region
ami_list = {
    'ap-northeast-1': 'ami-04e1075132b58d401',
    'ap-southeast-1': 'ami-0085d056966878386',
    'ap-southeast-2': 'ami-0362e087f9bc95eab',
    'eu-central-1': 'ami-073cbc06a519d841c',
    'eu-west-1': 'ami-0b7fd2a785a106c16',
    'us-east-1': 'ami-0dfff14193996f618',
    'us-west-1': 'ami-03a8de9005d02ebbd',
    'us-west-2': 'ami-0ed7044a16cb71007'
}


# function get new region that has the lowest spot instance price
def get_region_with_lowest():
    g2_spot_table = dynamodb.Table('DeepSpotCloud-G2SpotInstance-Price')

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

    user_data = 'checkpoint-file-path:deepspotcloud-cp-bucket/' + user_data_param

    response = client.request_spot_instances(

        SpotPrice='0.65',
        InstanceCount=1,

        Type='one-time',
        LaunchSpecification={

            'ImageId': ami_list[new_region],
            'KeyName': 'mjay',
            'InstanceType': 'g2.2xlarge',
            'SecurityGroupIds': ["sg-71ac970e"],
            'Placement': {
                'AvailabilityZone': new_az
            },
            'UserData': base64.b64encode(user_data.encode("ascii")).decode('ascii')
        }
    )
    return user_data


def lambda_handler(event, context):
    # 01. Request Params(user-data)
    ud = str(event.get('ud', None))

    # 02. get new region that has the lowest spot instance price
    new_az = get_region_with_lowest()

    sentence = "Starting new instance in " + new_az

    # 03. Call an API to request new spot instance
    user_data = start_new_instance(ud, new_az)

    print (sentence)
    print (user_data)
    return sentence
