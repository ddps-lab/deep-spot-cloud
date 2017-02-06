import boto3
import base64
client=boto3.client('ec2')

def lambda_handler(event, context):    # this lambda is for us-west-1 (N.California)(region)
    az='{}'.format(event['az'])        # for input parameters az=availability zone
    ud='{}'.format(event['ud'])        #  ud =user-data
    
    data= 'checkpoint-file-path:mj.bucket-1/' + ud        #mj.bucket-1 is s3 path information
       
    response = client.request_spot_instances(
       
        SpotPrice='0.65',
        InstanceCount=1,
       
        Type='one-time',
        LaunchSpecification={            
            
            'ImageId': 'ami-9cdb86fc',   # amis are all different in each every region 
            'KeyName': 'macbook-mj',     
            'InstanceType':'g2.2xlarge',
            'SecurityGroups': ['mj-security'],
            'Placement': {
            'AvailabilityZone': az    
            },
            'UserData': base64.b64encode(data.encode("ascii")).decode('ascii') 
            }
        )
    return "start new instance from us-west-1(N.California)"   
    
    
    ## In Amazon API Gateway have to set configuration in Integration Request -> add mapping templates as "application/json" and put
    ##   {
    ##      "az":$input.params('az'),
    ##      "ud":$input.params('ud')
    ##   }
    ## 