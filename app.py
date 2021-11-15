from flask import Flask, render_template, url_for, request, redirect, session
from Adafruit_IO import Client, MQTTClient
from requests.api import put
import pymongo
import datetime

import os
app = Flask(__name__)
picFolder = os.path.join('static')
app.config['UPLOAD_FOLDER'] = picFolder
pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'img4.jpg')
pic2 = os.path.join(app.config['UPLOAD_FOLDER'], 'img9.jpg')
# pic1=os.path.join(app.config['UPLOAD_FOLDER'],'bgimg.jpg')

dbconn = pymongo.MongoClient(
    "mongodb+srv://zappieruser:userpassword@luggagereg.qodbd.mongodb.net/LuggageReg?retryWrites=true&w=majority")
mydb = dbconn['LuggageReg']
mycol = mydb["luggagedb"]
nodes = mydb["trackdb"]
user = mydb["user"]
aio = Client('RedRabbit1', 'aio_gykX28Fv6J5XVu33poXHccsjwqaa')


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    #  if request.method == 'POST':
    #     pnr = request.form['pnr']
        # if (pnr in  nodes.find({})):
    return render_template('login.html' ,image=pic1)

@app.route("/registration", methods=['GET', 'POST'])
def reg():
    return render_template('registration.html', user_image=pic1)


@app.route("/read", methods=['GET', 'POST'])
def read():
    if request.method == 'POST':
        pnr = request.form['pnr']
        flightno = request.form['flightno']
        name = request.form['name']

        toggle = aio.feeds('rfidswitch')
        switch = aio.receive(toggle.key)
        if switch.value == 'on':
            aio.send_data(toggle.key, 'off')
        else:
            aio.send_data(toggle.key, 'on')

        data = aio.feeds('rfiddata')
        dataval = aio.receive(data.key)
        tagval = dataval.value
        dbgo = {"_id": pnr, "tag_id": tagval,
                "flightno": flightno, "name": name}
        nodego = {"_id": pnr, "tag_id": tagval, "location": [
            "checkin"], "lastNode": "checkin", 'lastSeen': datetime.datetime.utcnow()}
        mycol.insert_one(dbgo)
        nodes.insert_one(nodego)
        return render_template('confirmation.html', data=dataval.value, pnr=pnr, name=name, fno=flightno)
    else:
        return render_template('registration.html', user_image=pic1)


@app.route("/update", methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        pnr = request.form['pnr']
        flightno = request.form['flightno']
        name = request.form['name']

        toggle = aio.feeds('rfidswitch')
        switch = aio.receive(toggle.key)
        if switch.value == 'on':
            aio.send_data(toggle.key, 'off')
        else:
            aio.send_data(toggle.key, 'on')

        data = aio.feeds('rfiddata')
        dataval = aio.receive(data.key)
        tagval = dataval.value
        nodes.update_one({"_id": pnr}, {'$set': {'tag_id': tagval}})
        return render_template('confirmation.html', data=dataval.value, pnr=pnr, name=name, fno=flightno)
    else:
        return render_template('registration.html', user_image=pic1)


@app.route("/track", methods=['GET', 'POST'])
def track():
    tdata = nodes.find({}, {"_id": 1, 'lastNode': 1,'lastSeen': 1, 'tag_id': 1})
    return render_template('track.html', data=tdata)


@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        pnr = request.form['pnr']
        tdata = nodes.find({'_id': pnr}, {"_id": 1, 'lastNode': 1, 'lastSeen': 1, 'tag_id': 1})
        print(tdata)
        return render_template('track.html', data=tdata)


@app.route("/confirm", methods=['GET', 'POST'])
def confirm():
    return render_template('confirmation.html')

# @app.route("/user", methods=['GET', 'POST'])
# def user():
#     values =user.find({}, {"_id": 1, 'name': 1,'last_seen': 1})
#     return render_template('user.html', data=values)
