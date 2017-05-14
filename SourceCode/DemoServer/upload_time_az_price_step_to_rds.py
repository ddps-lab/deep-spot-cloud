import pymysql
import boto3
import json

# 0 AWS Resource Initialize
client = boto3.client('dynamodb')


def lambda_handler(event, context):
# 1 Get 3 Parameters from EC2
    param_az = str(event.get('az', 'us-east-1c'))
    param_step = str(event.get('step', 'Unknown'))
    param_current_time = (event.get('current_time', 'Unknown'))

    price = ""
# 2 From DynamoDB, get price associated with current instance
    response = client.get_item(TableName='g2-instance', Key={'az': {'S': param_az}})

    for keys, values in response.iteritems():
        if keys == "Item":
            for key, value in values.iteritems():
                if key == u'price':
                    a = value.values()

                    for i in a:
                        price = "$ " + i


# 3 Upload Status to Mysql Spottable
    mysql_spottable = pymysql.connect(host="mj3.xxxxxxxxx.us-east-1.rds.amazonaws.com", user="mj", passwd="xxxxxx",
                                      db="g2instance", connect_timeout=5)
    with mysql_spottable.cursor() as cur:

        cur.execute('insert into Spottable (Time, az, Price, step) values(%s,%s,%s,%s)',
                    (param_current_time, param_az, price, param_step))
        mysql_spottable.commit()

    mysql_spottable.close()

    return 0


