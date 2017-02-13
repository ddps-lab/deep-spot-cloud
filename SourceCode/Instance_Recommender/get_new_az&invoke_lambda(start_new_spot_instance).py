import boto3
import pprint
import base64
import pycurl
import cStringIO

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('g2-instance')

def lambda_handler(event, context):
    ud='{}'.format(event['ud'])
    response = table.scan()
    a_table={}
    for key, values in response.iteritems():
        if key=="Items":
            for i in values:
                a_table[str(i[u'az'])]=float(i[u'price'])
    
    new_az=min(a_table, key=a_table.get)  # return the key which has the lowest value
    new_region=new_az[:-1]
    
    buf = cStringIO.StringIO()
    c=pycurl.Curl()
    c.setopt(c.URL, 'xxxxx://xxxxxx.xxxxxxx.xxxxx.xxxx/xxxx/xxxx+new_region+xxx+new_az+xxxxx+ud+xxx')               
    c.setopt(c.WRITEFUNCTION, buf.write)
    c.perform()
    temp=buf.getvalue()
    c.close()

    return temp   ## e.g "Starting a new instance in xx-xxxx-x"     
    
    
   
