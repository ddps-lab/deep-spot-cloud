from datetime import datetime, timedelta
import pymysql
import boto3
# import json
# import time

dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('g2-instance')


def lambda_handler(event, context):
    conn = pymysql.connect(host="xxx.xxxxx.xxxx.rds.amazonaws.com", user="xx", passwd="xxxxxx",
                           db="g2instance", connect_timeout=5)

    local = '{}'.format(event['local'])

    response = table.scan()

    result = {}

    for key, values in response.iteritems():

        if key == "Items":

            for i in values:
                temp = i[u'price'][:-1]

                price = temp[1:]

                result[str(i[u'az'])] = str("$ " + i[u'price'])

    with conn.cursor() as cur:

        cur.execute("select * from Spottable ORDER BY Time DESC LIMIT 1")

        rows = cur.fetchall()

        item = rows[0]

        temp_time = datetime.strptime(str(item[0]), "%Y-%m-%d %H:%M:%S")

        utc_time = temp_time + timedelta(hours=int(local))

        time_dif = ("+" + str(local)) if int(local) >= 0 else ("-" + str(local))

        result['time'] = str(utc_time.strftime("%Y.%m.%d %H:%M:%S")) + " UTC " + time_dif

        result['az'] = item[1]

        result['price'] = item[2]

        result['step'] = item[3]


    cur.close()

    conn.close()

    conn = pymysql.connect(host="xxx.xxxxx.xxxx.rds.amazonaws.com", user="xx", passwd="xxxx",
                           db="migration", connect_timeout=5)

    with conn.cursor() as cur:

        cur.execute("select az from Route ORDER BY id ASC")

        rows = cur.fetchall()

        for row in rows:
            ids = result.get('migration', [])

            ids.append(row)

            result['migration'] = ids

    newlist = ' -> '.join(map(str, result['migration']))

    # print (newlist)

    result['migration'] = newlist

    cur.close()

    conn.close()

    return result



