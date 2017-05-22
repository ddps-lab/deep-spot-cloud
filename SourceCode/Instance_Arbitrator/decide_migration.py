import boto3
from boto3.dynamodb.conditions import Key, Attr

# AWS Resource Init
dynamodb = boto3.resource('dynamodb')


def lambda_handler(event, context):
    p_price = None
    # 1 get az parameter
    param_az = str(event.get('az', 'Unknown'))

    g2_spot_table = dynamodb.Table('g2-instance')
    # 2 fetch az that has the lowest price from DynamoDB
    temp_table = {}
    response = g2_spot_table.scan()

    for key, values in response.iteritems():

        if key == "Items":

            for i in values:
                temp_table[str(i[u'az'])] = float(i[u'price'])

    az_with_lowest = min(temp_table, key=temp_table.get)  # return the key which has the lowest value

    lowest_price = temp_table[az_with_lowest]

    # 3 and get price from current instance from DynamoDB
    response = g2_spot_table.query(
        KeyConditionExpression=Key('az').eq(param_az)
    )
    for i in response['Items']:
        p_price = i['price']

    # 4 Compare Price and Show Result
    print ("information about lowest")
    print (az_with_lowest)
    print (lowest_price)

    print("current running instance's information")
    print param_az
    print (p_price)

    price_difference = float(p_price) - float(lowest_price)

    print ("price difference")
    print (price_difference)

    print ("migration needed?")

    if price_difference >= 0.0800:
        print ("Yes")
        return True
    else:
        print ("No")
        return False
