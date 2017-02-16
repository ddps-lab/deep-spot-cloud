import sys
import logging

import pymysql
import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('g2-instance')

conn = pymysql.connect(host="xx.xxxx.xxxxxx.rds.amazonaws.com", user="mj", passwd="xxxxx", db="g2instance", connect_timeout=5)

def lambda_handler(event, context):


    response = table.scan()
    result={}
    for key, values in response.iteritems():
        if key=="Items":
            for i in values:
                # a=a[:-1]
                # az=a[1:]
                temp=i[u'price'][:-1]
                price=temp[1:]
                result[str(i[u'az'])]=str("$"+i[u'price'])
    
    with conn.cursor() as cur:
        
        
        cur.execute("select * from Spottable ORDER BY Time DESC LIMIT 1")
        rows = cur.fetchall()
    
        for row in rows:
           
            result['time'] = str(row[0])+" UTC"
            result['az'] = row[1]
            result['price'] = row[2]
            result['step'] = row[3]
            
            return result

        
