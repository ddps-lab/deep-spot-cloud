import sys
import logging

import pymysql
import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('g2-instance')

<<<<<<< HEAD
conn = pymysql.connect(host="mj.cajasrj4yypo.us-east-1.rds.amazonaws.com", user="mj", passwd="xxxxx", db="g2instance", connect_timeout=5)
=======
conn = pymysql.connect(host="xx.xxxx.xxxxxx.rds.amazonaws.com", user="mj", passwd="xxxxx", db="g2instance", connect_timeout=5)
>>>>>>> b069063f9822dde327f1a32d2d0e364e20dc0ed0

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
                result[str(i[u'az'])]=str(i[u'price']+"$")
    
    with conn.cursor() as cur:
        
        
        cur.execute("select * from Spottable ORDER BY Time DESC LIMIT 1")
        rows = cur.fetchall()
    
        for row in rows:
           
            result['time'] = str(row[0])
            result['az'] = row[1]
            result['price'] = row[2]
            result['step'] = row[3]
            
            return result

        
