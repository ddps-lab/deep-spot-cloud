import sys
import logging
import pymysql
import boto3
import json
client=boto3.client('dynamodb')

def lambda_handler(event, context):
    conn = pymysql.connect(host="xxxxxxxxxxxxxxxxxxxx", user="mj", passwd="******", db="g2instance", connect_timeout=5)
    az=json.dumps('{}'.format(event['az']))
    step=json.dumps('{}'.format(event['step']))
    current_time=json.dumps('{}'.format(event['current_time']))

    a=str(az)
    a=a[:-1]
    az=a[1:]

    price=""

    response = client.get_item(TableName='g2-instance', Key={'az':{'S':az}})
    for keys, values in response.iteritems():
        if keys == "Item":
            for key, value in values.iteritems():
                if key==u'price':
                    a=value.values()
                    for i in a:
                        price="$ "+i

    b=str(step)
    b=b[:-1]
    step=b[1:]

    c=str(current_time)
    c=c[:-1]
    current_time=c[1:]



    with conn.cursor() as cur:

        cur.execute('insert into Spottable (Time, AZ, Price, Step) values(%s,%s,%s,%s)',(current_time,az,price,step))

        conn.commit()
    cur.close()
    conn.close() 

        return 0
