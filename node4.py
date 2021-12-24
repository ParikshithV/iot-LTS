from Adafruit_IO import Client, MQTTClient
import pymongo
import datetime
# dbconn = pymongo.MongoClient("mongodb+srv://zappieruser:userpassword@luggagetracking.qodbd.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
dbconn = pymongo.MongoClient()
mydb = dbconn['luggageTracking']
nodes = mydb["trackdb"]
aio = Client('RedRabbit1', 'aio_gykX28Fv6J5XVu33poXHccsjwqaa')
temp=0


ADAFRUIT_IO_KEY = 'aio_gykX28Fv6J5XVu33poXHccsjwqaa'

ADAFRUIT_IO_USERNAME = 'RedRabbit1'

FEED_ID = 'node4'

def connected(client):
    print('Connected to Adafruit IO!  Listening for {0} changes...'.format(FEED_ID))
    client.subscribe(FEED_ID)

def subscribe(client, userdata, mid, granted_qos):
    print('Subscribed to {0} with QoS {1}'.format(FEED_ID, granted_qos[0]))

def disconnected(client):
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    global temp
    if temp!=payload:
        nodes.update_one({"_id" : payload}, {'$push': {'location': 'node4'}})
        nodes.update_one({"_id" : payload}, {'$set': {'lastNode': 'node4'}})
        nodes.update_one({"_id" : payload}, {'$set': {'status': 'boarding'}})
        nodes.update_one({"_id" : payload}, {'$set': {'lastSeen': datetime.datetime.utcnow()}})
    else:
        print('Tag scan repeated')
    temp=payload
    print('Feed {0} received new value: {1}'.format(feed_id, payload))

client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message
client.on_subscribe  = subscribe

client.connect()

client.loop_blocking()