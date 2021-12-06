from Adafruit_IO import Client, MQTTClient
import pymongo
import datetime
dbconn = pymongo.MongoClient("mongodb+srv://zappieruser:userpassword@luggagereg.qodbd.mongodb.net/LuggageReg?retryWrites=true&w=majority")
mydb = dbconn['LuggageReg']
nodes = mydb["trackdb"]
aio = Client('RedRabbit1', 'aio_gykX28Fv6J5XVu33poXHccsjwqaa')


ADAFRUIT_IO_KEY = 'aio_gykX28Fv6J5XVu33poXHccsjwqaa'

ADAFRUIT_IO_USERNAME = 'RedRabbit1'

FEED_ID = 'node1'

def connected(client):
    print('Connected to Adafruit IO!  Listening for {0} changes...'.format(FEED_ID))
    client.subscribe(FEED_ID)

def subscribe(client, userdata, mid, granted_qos):
    print('Subscribed to {0} with QoS {1}'.format(FEED_ID, granted_qos[0]))

def disconnected(client):
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    nodes = mydb['trackdb']
    nodes.update_one({"tag_id" : payload}, {'$push': {'location': 'node1'}})
    nodes.update_one({"tag_id" : payload}, {'$set': {'lastNode': 'node1'}})
    nodes.update_one({"tag_id" : payload}, {'$set': {'lastSeen': datetime.datetime.utcnow()}})
    print('Feed {0} received new value: {1}'.format(feed_id, payload))

client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message
client.on_subscribe  = subscribe

client.connect()

client.loop_blocking()