import boto3
import pymysql


def lambda_handler(event, context):

    #spot_id = None

    conn = pymysql.connect(host="xxxx.xxxx.xxxxx.xxx.xxxx.com", user="xxx", passwd="xxxxx",
                           db="migration", connect_timeout=5)

    with conn.cursor() as cur:
        cur.execute("select instance_id , region from Route ORDER BY id DESC LIMIT 1")

        rows = cur.fetchall()

        item = rows[0]

        c_region = item[1]

        c_instance_id = item[0]

        print (c_region)

        print (c_instance_id)

    cur.close()
    conn.close()

    sentence = "Terminating in " + c_region

    ec2 = boto3.resource('ec2', region_name=c_region)

    instances = ec2.instances.filter(

        Filters=[{'Name': 'instance-id', 'Values': [c_instance_id]}]
    )

    for instance in instances:

        # spot_id=instance.spot_instance_request_id   #alternatively you can use spot_request_id and cancel spot request but it doesn't shut down running ec2 instance

        instance.terminate()  # terminating enables Request Spot Instance to cancel itself automatically

        # print (instance)

        # for i in instance.tags:

        # spot_id=i[u'Value']          # It's for the Spot Fleet Request It has tags including sfr-id(spot fleet request), and with this you can cancel spot fleet request including terminating ec2 instance contray to spot instance request

    # client = boto3.client('ec2', region_name=c_region)
    # response = client.cancel_spot_instance_requests(
    #     SpotInstanceRequestIds=[
    #     spot_id,                      # It's canceling spot instance reuqest
    #     ],

    # )


    return sentence