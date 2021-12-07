from flask import Flask, render_template, request, session
from Adafruit_IO import Client, MQTTClient
from requests.api import put
import pymongo
import datetime
import os

app = Flask(__name__)
app.secret_key = '2021'
picFolder = os.path.join('static')
app.config['UPLOAD_FOLDER'] = picFolder
pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'img4.jpg')
pic2 = os.path.join(app.config['UPLOAD_FOLDER'], 'img9.jpg')

# dbconn =  pymongo.MongoClient("mongodb+srv://zappieruser:userpassword@luggagetracking.qodbd.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
dbconn = pymongo.MongoClient()
mydb = dbconn['luggageTracking']
feedbk = mydb["feedback"]
mycol = mydb["luggagedb"]
nodes = mydb["trackdb"]
aio = Client('RedRabbit1', 'aio_gykX28Fv6J5XVu33poXHccsjwqaa')


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route("/feedback", methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        pnr = request.form['pnr']
        feed = request.form['feed']
        send = {"pnr": pnr, "name": name, "feedback": feed}
        feedbk.insert_one(send)
        tdata = nodes.find({'pnr': pnr}, {"_id": 1, 'lastNode': 1, 'lastSeen': 1, 'pnr': 1, 'name': 1, 'location': 1})
        return render_template('userdash.html', data=tdata)
    else:
        name = session["name"]
        pnr = session["pnr"]
        return render_template('feedback.html', name=name, pnr=pnr)


@app.route("/d_feedback", methods=['GET', 'POST'])
def d_feedback():
        fdata = feedbk.find({}, {"pnr": 1, 'name': 1,'feedback': 1})
        return render_template('display_feed.html', fdata=fdata)

@app.route("/adminlogin", methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        if (name=='admin' and password=='pesu'):
            session['admin'] = 'admin'
            tdata = nodes.find({}, {"pnr": 1, 'lastNode': 1,'lastSeen': 1, 'pnr': 1, 'location': 1})
            return render_template('track.html', data=tdata)
        else:
            return render_template('alogin.html', user_image=pic1, err="alert")
    else:
        return render_template('alogin.html', user_image=pic1)

@app.route("/userlogin", methods=['GET', 'POST'])
def userlogin():
    if request.method == 'POST':
        pnr = request.form['pnr']
        name = request.form['name']
        try:
            pnrdata = mycol.find_one({'name':name}, {"_id": 1, 'name': 1})['name']
            if pnrdata == name:
                session['user'] = 'user'
                session['pnr'] = pnr
                session['name'] = name
                tdata = nodes.find({'pnr': pnr}, {"_id": 1, 'lastNode': 1, 'lastSeen': 1, 'pnr': 1, 'name': 1, 'location': 1})
                return render_template('userdash.html', data=tdata)
            else:
                return render_template('userdash.html', user_image=pic1, err="alert")
        except:
            return render_template('ulogin.html', user_image=pic1, err="alert")
    else:
        return render_template('ulogin.html', user_image=pic1)

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
        return render_template('confirmation.html',user_image=pic1, data=dataval.value, pnr=pnr, name=name, fno=flightno)
    else:
        return render_template('registration.html', user_image=pic1)


@app.route("/update", methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        pnr = request.form['pnr']
        flightno = request.form['flightno']
        name = request.form['name']
        tagdata = request.form['data']
        dbgo = {"_id": tagdata, "pnr": pnr, "flightno": flightno, "name": name}
        nodego = {"_id": tagdata, "pnr": pnr, "location": ["checkin"], "lastNode": "checkin", "status":"checkin", "flightno":flightno, 'lastSeen': datetime.datetime.utcnow()}
        try:
            mycol.insert_one(dbgo)
            nodes.insert_one(nodego)
        except:
            return render_template('confirmation.html',user_image=pic1, data=tagdata, pnr=pnr, name=name, fno=flightno, err="Swal.fire")
        return render_template('confirmation.html',user_image=pic1, data=tagdata, pnr=pnr, name=name, fno=flightno)
    else:
        return render_template('registration.html', user_image=pic1)


@app.route("/track", methods=['GET', 'POST'])
def track():
    if 'admin' in session:
        tdata = nodes.find({}, {"_id": 1, 'lastNode': 1, 'flightno': 1,'lastSeen': 1, 'pnr': 1, 'location': 1})
        return render_template('track.html', data=tdata)
    else:
        return render_template('alogin.html', user_image=pic1)


@app.route("/search", methods=['GET', 'POST'])
def search():
    if 'admin' in session:
        if request.method == 'POST':
            pnr = request.form['pnr']
            tdata = nodes.find({'pnr': pnr}, {"_id": 1, 'lastNode': 1, 'flightno': 1, 'lastSeen': 1, 'pnr': 1, 'location': 1})
            return render_template('track.html', data=tdata)
    else:
        return render_template('alogin.html', user_image=pic1)

@app.route("/boarding", methods=['GET', 'POST'])
def boarding():
    return("Working on it")

@app.route("/confirm", methods=['GET', 'POST'])
def confirm():
    return render_template('confirmation.html',user_image=pic1)

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session.clear()
    return render_template('home.html')
