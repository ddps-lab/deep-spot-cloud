from __future__ import print_function

import ast

import boto3

import pymysql

client = boto3.client('ec2')


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

    print(c_az)

    print(c_region)

    print(c_instance_id)

    print(message)

    conn = pymysql.connect(host="xxxxxx", user="xit x", passwd="xxxxxxxx",
                           db="migration", connect_timeout=5)
    with conn.cursor() as cur:

        cur.execute('insert into Route (instance_id, region, az) values(%s,%s,%s)',
                    (c_instance_id, c_region, c_az))
        conn.commit()

    cur.close()
    conn.close()

    return 0
