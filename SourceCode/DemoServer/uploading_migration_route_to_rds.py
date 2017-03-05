from __future__ import print_function

import ast

import boto3

import pymysql

def lambda_handler(event, context):

    c_instance_id = None

    c_region = None

    c_az = None

    message = (event['Records'][0]['Sns']['Message'])

    d = ast.literal_eval(message)

    for key, value in d.iteritems():

        if key == "region":
            c_region = value

        if key == "detail":

            for i, j in value.iteritems():

                if i == "instance-id":
                    print(j)

                    print(type(j))

                    c_instance_id = j

    client = boto3.client('ec2', region_name=c_region)

    response = client.describe_instances(

        InstanceIds=[
            c_instance_id,
        ],

    )

    for key, value in response.iteritems():

        if key == "Reservations":

            for i in value:  # value has 5 indexes

                for j in (i['Instances']):
                    c_az = j[u'Placement'][u'AvailabilityZone']


    dynamo=boto3.client('dynamodb')

    c_price=""

    response = dynamo.get_item(TableName='g2-instance', Key={'az':{'S':c_az}})

    for keys, values in response.iteritems():
        if keys == "Item":
            for key, value in values.iteritems():
                if key==u'price':
                    a=value.values()

                    for i in a:

                        c_price="$ "+i

    print(c_az)
    print(type(c_az))
    print(c_region)
    print(type(c_region))
    print(c_instance_id)
    print(type(c_instance_id))
    print (message)
    print(c_price)
    print (type(c_price))

    conn = pymysql.connect(host="xxxxxxxxxx", user="xxxx", passwd="xxxxxx",
                           db="migration", connect_timeout=5)
    with conn.cursor() as cur:

        cur.execute('insert into Route (instance_id, region, az, price) values(%s,%s,%s,%s)',
                    (c_instance_id, c_region, c_az, c_price))
        conn.commit()

    cur.close()
    conn.close()


    return 0
