from datetime import datetime, timedelta, timezone
import boto3
import pymysql

# 00. AWS Resource Initialize
dynamodb = boto3.resource('dynamodb')


# 01. UTC to Local Converter
def convert_utc_to_local(utctime_str, offset):
    return datetime.strptime(utctime_str, "%Y-%m-%d %H:%M:%S") \
        .replace(tzinfo=timezone.utc).astimezone(tz=timezone(timedelta(hours=offset))) \
        .strftime("%Y-%m-%d %H:%M:%S %Z")


def lambda_handler(event, context):
    # 02. MySQL and DynamoDB Instance
    mysql_g2_obj = pymysql.connect(host="mj3.xxxxxx.us-east-1.rds.amazonaws.com",
                                   user="mj", passwd="xxxxx", db="g2instance", connect_timeout=5)
    mysql_migration_obj = pymysql.connect(host="mj3.xxxxx.us-east-1.rds.amazonaws.com", user="mj",
                                          passwd="xxxx",
                                          db="migration", connect_timeout=5)
    dynamo_obj = dynamodb.Table('g2-instance')

    # 03. Request Params
    param_local = int(event.get('local', 0))

    # 04. Get current pricetable
    pricetable = dynamo_obj.scan()
    resp_pricetable_dict = {}
    for item in pricetable["Items"]:
        resp_pricetable_dict[str(item['az'])] = item['price']

    # 05. Get last information (Current az, current price of az, current steps, last update time)
    with mysql_g2_obj.cursor() as cur:
        resp_lastinfo_dict = {}

        cur.execute("select * from Spottable ORDER BY Time DESC LIMIT 1")
        try:
            row = cur.fetchall()[0]

            resp_lastinfo_dict["time"] = convert_utc_to_local(str(row[0]), param_local)
            resp_lastinfo_dict["az"] = row[1]
            resp_lastinfo_dict["price"] = row[2]
            resp_lastinfo_dict["step"] = int(row[3])
        except:
            pass

    mysql_g2_obj.close()

    # 06. Get migration route
    with mysql_migration_obj.cursor() as cur:
        resp_migration_list = []

        cur.execute("select az,current_price,time from Route ORDER BY id ASC")

        rows = cur.fetchall()
        for row in rows:
            resp_migration_list.append({
                "az": str(row[0]),
                "price": row[1],
                "time": convert_utc_to_local(str(row[2]), param_local) if row[2] else None
            })

    mysql_migration_obj.close()

    # 07. Return JSON
    return {
        "pricetable": resp_pricetable_dict,
        "lastinfo": resp_lastinfo_dict,
        "migration": resp_migration_list
    }

