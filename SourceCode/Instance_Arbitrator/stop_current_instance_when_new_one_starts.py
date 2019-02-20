import boto3
import pymysql
import time


def lambda_handler(event, context):
    # 00 to let new instance starts before termination happends
    time.sleep(120)

    # 01 Mysql Instance
    mysql_migration = pymysql.connect(host="xxxxxxxxx.us-west-2.rds.amazonaws.com",
                                      user="deepspotcloud",
                                      passwd="xxxxxx",
                                      db="migration", connect_timeout=5)

    # 02 fetch current running instance from Mysql
    with mysql_migration.cursor() as cur:
        cur.execute("select instance_id , az from Route ORDER BY id DESC LIMIT 2")

        rows = cur.fetchall()[1]

        item = rows

        c_region = item[1][:-1]

        c_instance_id = item[0]

        print ("instance to be terminated")
        print (c_instance_id)
        print (c_region)

    mysql_migration.close()

    current_status = "Terminating in " + c_region

    # 03 Call An API to terminate instance
    ec2 = boto3.resource('ec2', region_name=c_region)

    instances_to_terminate = ec2.instances.filter(

        Filters=[{'Name': 'instance-id', 'Values': [c_instance_id]}]
    )

    for instance in instances_to_terminate:
        instance.terminate()

    print (current_status)
    return current_status
