from __future__ import print_function

import ast

import boto3

import pymysql

from boto3.dynamodb.conditions import Key, Attr


def lambda_handler(event, context):
    p_id = None

    p_az = None

    p_price = None

    c_instance_id = None

    c_region = None

    c_az = None

    c_price = None

    instance_time = None

    # 01 mysql migration instance to fetch prveious instance
    mysql_migration_object = pymysql.connect(host="mj3.xxxxxx.us-east-1.rds.amazonaws.com", user="mj",
                                             passwd="xxxxx",
                                             db="migration", connect_timeout=5)
    with mysql_migration_object.cursor() as cur:
        try:
            cur.execute("select id, az from Route ORDER BY id DESC LIMIT 1")

            rows = cur.fetchall()

            item0 = rows[0]

            p_id = item0[0]

            p_az = item0[1]
        except:
            pass

    mysql_migration_object.close()

    # 02 get instance_id , time, region from AWS SNS Services

    message_from_sns_service = (event['Records'][0]['Sns']['Message'])

    dict_message = ast.literal_eval(message_from_sns_service)

    for key, value in dict_message.iteritems():

        if key == "region":
            c_region = value
        if key == "time":
            instance_time = value
        if key == "detail":

            for i, j in value.iteritems():

                if i == "instance-id":
                    c_instance_id = j

                    # 03 call an API to get instance availability zone
    client = boto3.client('ec2', region_name=c_region)

    instance_information = client.describe_instances(

        InstanceIds=[
            c_instance_id,
        ],

    )
    for key, value in instance_information.iteritems():

        if key == "Reservations":

            for i in value:  # value has 5 indexes

                for j in (i['Instances']):
                    c_az = j[u'Placement'][u'AvailabilityZone']

                    # 04 get previous and current instance's price
    dynamodb = boto3.resource('dynamodb')

    try:
        g2_spot_table = dynamodb.Table('g2-instance')

        price_for_p_az = g2_spot_table.query(
            KeyConditionExpression=Key('az').eq(p_az)
        )
        for i in price_for_p_az['Items']:
            p_price = i['price']
            p_price = float(p_price.replace(u'\N{MINUS SIGN}', '-'))
    except:
        pass

    price_for_c_az = g2_spot_table.query(
        KeyConditionExpression=Key('az').eq(c_az)
    )
    for i in price_for_c_az['Items']:
        c_price = i['price']
        c_price = float(c_price.replace(u'\N{MINUS SIGN}', '-'))

    # 05 print status
    print("p_id is -> " + str(p_id))

    print("p_az is -> " + (str(p_az)))

    print("p_price -> " + str(p_price))

    print("c_instance_id -> " + c_instance_id)

    print("c_az is -> " + c_az)

    print("c_price -> " + str(c_price))

    print("time is -> " + instance_time)

    # 06 put price in previous instance and upload information about current instance
    mysql_migration_object1 = pymysql.connect(host="mj3.xxxxx.us-east-1.rds.amazonaws.com", user="mj",
                                              passwd="xxxxx",
                                              db="migration", connect_timeout=5)
    with mysql_migration_object1.cursor() as cur:

        cur.execute('insert into Route (instance_id, az, current_price, time) values(%s,%s,%s,%s)',
                    (c_instance_id, c_az, c_price, instance_time))
        try:
            cur.execute("UPDATE Route SET previous_price=%s WHERE id=%s", (p_price, int(p_id)))
        except:
            pass
        mysql_migration_object1.commit()

    mysql_migration_object1.close()

    return 0
