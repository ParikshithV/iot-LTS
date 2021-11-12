from flask import Flask, render_template, url_for, request, redirect, session
from Adafruit_IO import Client, MQTTClient
from requests.api import put
import pymongo
import datetime

dbconn = pymongo.MongoClient("mongodb+srv://zappieruser:userpassword@luggagereg.qodbd.mongodb.net/LuggageReg?retryWrites=true&w=majority")
mydb = dbconn['LuggageReg']
mycol = mydb["luggagedb"]
nodes = mydb["trackdb"]

aio = Client('RedRabbit1', 'aio_gykX28Fv6J5XVu33poXHccsjwqaa')
app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def get():
    return render_template('registration.html')

@app.route("/registration", methods=['GET', 'POST'])
def reg():
    return render_template('registration.html')


@app.route("/read", methods=['GET', 'POST'])
def read():
    if request.method == 'POST':
        pnr = request.form['pnr']
        flightno = request.form['flightno']
        name = request.form['name']

        toggle = aio.feeds('rfidswitch')
        switch = aio.receive(toggle.key)
        switchval = switch
        if switch.value == 'on':
            aio.send_data(toggle.key, 'off')
        else:
            aio.send_data(toggle.key, 'on')

        data = aio.feeds('rfiddata')
        dataval = aio.receive(data.key)
        tagval=dataval.value
        dbgo = { "_id" : pnr, "tag_id" : tagval, "flightno" : flightno, "name" : name}
        nodego = { "_id" : pnr, "tag_id" : tagval, "location" : ["checkin"], "lastNode": "checkin", 'lastSeen': datetime.datetime.utcnow()}
        mycol.insert_one(dbgo)
        nodes.insert_one(nodego)
        return render_template('confirmation.html', data=dataval.value, pnr=pnr, name=name)
    else:
        return render_template('registration.html')

@app.route("/update", methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        pnr = request.form['pnr']
        data = request.form['tagid']
        name = request.form['name']

        toggle = aio.feeds('rfidswitch')
        switch = aio.receive(toggle.key)
        if switch.value == 'on':
            aio.send_data(toggle.key, 'off')
        else:
            aio.send_data(toggle.key, 'on')

        data = aio.feeds('rfiddata')
        dataval = aio.receive(data.key)
        nodes.update_one({"_id" : pnr}, {'$set': {'tag_id': data}})
        return render_template('confirmation.html', data=data, pnr=pnr, name=name)
    else:
        return render_template('registration.html')