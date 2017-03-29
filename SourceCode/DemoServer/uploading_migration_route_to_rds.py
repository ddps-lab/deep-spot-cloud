from __future__ import print_function

import ast

import boto3

import pymysql

from boto3.dynamodb.conditions import Key, Attr


def lambda_handler(event, context):
    p_id = None

    p_az = None

    p_price = ""

    c_instance_id = None

    c_region = None

    c_az = None

    c_price = ""

    instance_time = None

    conn = pymysql.connect(host="xxxxx.us-east-1.rds.amazonaws.com", user="mj", passwd="xxx",
                           db="migration", connect_timeout=5)
    with conn.cursor() as cur:

        cur.execute("select id, az from Route ORDER BY id DESC LIMIT 1")

        rows = cur.fetchall()

        item0 = rows[0]

        p_id = item0[0]

        p_az = item0[1]

    cur.close()
    conn.close()
    message = (event['Records'][0]['Sns']['Message'])

    d = ast.literal_eval(message)

    for key, value in d.iteritems():

        if key == "region":
            c_region = value
        if key == "time":
            instance_time = value
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

    # dynamo=boto3.client('dynamodb')

    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('g2-instance')

    response = table.query(
        KeyConditionExpression=Key('az').eq(p_az)
    )
    for i in response['Items']:
        p_price = "$ " + i['price']

        # =current_az_price

    response = table.query(
        KeyConditionExpression=Key('az').eq(c_az)
    )
    for i in response['Items']:
        c_price = "$ " + i['price']

        # c_price=current_az_price

    print("p_id is -> " + str(p_id))
    print(type(p_id))

    print("p_az is -> " + p_az)
    print(type(p_az))

    print("p_price -> " + p_price)
    print(type(p_price))

    print("c_instance_id -> " + c_instance_id)
    print(type(c_instance_id))

    print("c_az is -> " + c_az)
    print(type(c_az))

    print("c_price -> " + c_price)
    print(type(c_price))

    print("time is -> " + instance_time)
    print(type(instance_time))

    conn = pymysql.connect(host="xxxx.us-east-1.rds.amazonaws.com", user="mj", passwd="xxxx",
                           db="migration", connect_timeout=5)
    with conn.cursor() as cur:

        cur.execute("UPDATE Route SET old_price=%s WHERE id=%s", (p_price, int(p_id)))
        cur.execute('insert into Route (instance_id, az, price,time) values(%s,%s,%s,%s)',
                    (c_instance_id, c_az, c_price, instance_time))
        conn.commit()

    cur.close()
    conn.close()

    return 0
