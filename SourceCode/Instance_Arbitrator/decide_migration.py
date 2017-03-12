import boto3

dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('g2-instance')

from boto3.dynamodb.conditions import Key, Attr


def lambda_handler(event, context):
    p_price = None
    az = '{}'.format(event['az'])
    # az="us-east-1c"
    response = table.scan()

    a_table = {}

    for key, values in response.iteritems():

        if key == "Items":

            for i in values:
                a_table[str(i[u'az'])] = float(i[u'price'])

    lowest_az = min(a_table, key=a_table.get)  # return the key which has the lowest value

    lowest_price = a_table[lowest_az]
    print ("information about lowest")
    print (lowest_az)
    print (lowest_price)

    response = table.query(
        KeyConditionExpression=Key('az').eq(az)
    )
    for i in response['Items']:
        p_price = i['price']
    print("current running instance's information")
    print az
    print (p_price)
    print (type(p_price))

    print ("diff")
    print (float(p_price) - float(lowest_price))
    print (float(p_price) - float(lowest_price) >= 0.0800)
    if (float(p_price) - float(lowest_price) >= 0.0800):
        return True
    else:
        return False
        # return (lowest_price)