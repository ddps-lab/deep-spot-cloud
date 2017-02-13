import sys
import logging

import pymysql
import boto3
import json

conn = pymysql.connect(host="mj.cajasrj4yypo.us-east-1.rds.amazonaws.com", user="mj", passwd="2018year", db="g2instance", connect_timeout=5)

def lambda_handler(event, context):
    with conn.cursor() as cur:
        cur.execute("select * from Spottable ORDER BY Time DESC LIMIT 1")
        rows = cur.fetchall()

        for row in rows:
            result = {}
            result['time'] = str(row[0])
            result['az'] = row[1]
            result['price'] = row[2]
            result['step'] = row[3]
            return result
