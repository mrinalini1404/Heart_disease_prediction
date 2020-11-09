import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from flask import Flask, render_template,request, redirect, url_for, session,Response
import pymysql
import re
import json
import time
import joblib
import os
import numpy as np
import pickle
from datetime import datetime
import requests
from flask import Flask, jsonify, request
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, wfdb, cv2
from wfdb import processing
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
global graph
graph =tf.compat.v1.get_default_graph()
from werkzeug.utils import secure_filename
import numpy as np
import tensorflow as tf
from keras.models import load_model
loaded_model = load_model('models/cnn_5labels_7.h5')

app = Flask(__name__)
app.secret_key = 'Mrinalini'

def get_db_result(sql):
    connection = pymysql.connect(host='127.0.0.1',
                                 user='root',
                                 password='root',
                                 db='healthtracker')
    print(sql)
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)
            connection.close()

    except:
        return []

    return result

def get_db_result_as_dict(sql):
    return dict((x, y) for x, y in get_db_result(sql))

def execute_db(sql):
    connection = pymysql.connect(host='127.0.0.1',
                                 user='root',
                                 password='root',
                                 db='healthtracker')
    print(sql)
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            connection.commit()
            connection.close()
    except:
        pass

@app.route('/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        sql = "select * from accounts where username = '"+username+"' and password = '"+password+"'";
        account = get_db_result(sql)
        # If account exists in accounts table in out database
        print(account)
        if (account):
            print(account)
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account[0][0]
            session['username'] = account[0][1]
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)  
     
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        sql = "select * from accounts where username = '"+username+"'";
        account = get_db_result(sql)
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            sql = "insert into accounts values(NULL, '"+username+"' , '"+password+"','"+email+"')";
            execute_db(sql)
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

@app.route('/home',methods=['GET'])
def home():
    if 'loggedin' in session:
        return render_template('home.html')
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        file1 = request.files['file1']
        filename = secure_filename(file.filename)
        filename1 = secure_filename(file1.filename)
        file.save(os.path.join('upload', filename))
        file.save(os.path.join('upload', filename1))
        return redirect(url_for('prediction', filename=os.path.splitext(filename)[0]))
    return render_template('upload.html')

# For MIT-BIH Data
@app.route('/prediction/<filename>')
def prediction(filename):
    print(filename)
    file_path = 'uploads/'+filename 
    start = 0
    stop = 65000
    record = wfdb.rdrecord(file_path, sampfrom=start, sampto=stop, channels=[0])
    ecg = record.p_signal
    rqrs = processing.xqrs_detect(record.p_signal[:,0], record.fs)
    
    test_data = []
    for i in range(1, 100):
        start = rqrs[i]
        stop = rqrs[i]+200
        if start<0: 
            start=0
        temp_rec = wfdb.rdrecord(file_path, sampfrom=start,sampto=stop, channels=[0])
        image = plt.figure()
        plt.plot(range(200), temp_rec.p_signal)
        image.canvas.draw()
        data = np.frombuffer(image.canvas.tostring_rgb(), dtype=np.uint8)
        data = data.reshape((image.canvas.get_width_height()[::-1] + (3,)))
        data = cv2.cvtColor(data, cv2.COLOR_RGB2BGR)
        data = cv2.resize(data, (432, 288), cv2.INTER_LINEAR)
        data = data[288-250:288-35, 55:390]
        data = cv2.resize(data, (int(215/5), int(215/5)), cv2.INTER_LINEAR)
        test_data.append(data)
        plt.savefig('images/'+str(i)+'.png')
        plt.close()
    test_data = np.array(test_data)

    # Convert List to Numpy Array
    test_data = np.array(test_data)

    with graph.as_default():
        predictions = loaded_model.predict_classes(test_data).tolist()
    for n, i in enumerate(predictions):
        if(i==0):
            predictions[n]='N'
        elif(i==1):
            predictions[n]='S'
        elif(i==2):
            predictions[n]='V'
        elif(i==3):
            predictions[n]='F'
        else:
            predictions[n]='Q'
    predictions=CountFrequency(predictions)   
    result=max(predictions, key=predictions.get) 
    if(predictions['S']==0 and predictions['V']==0 and predictions['F']==0 and predictions['Q']==0):
        result+=' with Normal'
    else:
        result+=' with Arrithmiya'
    return render_template('predict.html', predictions=predictions, result=result)

def CountFrequency(my_list):
    freq = {'S':0,'V':0,'F':0,'Q':0} 
    for item in my_list: 
        if (item in freq): 
            freq[item] += 1
        else: 
            freq[item] = 1
  
    return freq
    
@app.route('/profile')
def profile():
    if 'loggedin' in session:
        sql="select * from accounts where id= '"+str(session['id'])+"'"
        account = get_db_result(sql)
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/test_heart')
def test_heart():
    if 'loggedin' in session:
        sql="select * from accounts where id= '"+str(session['id'])+"'"
        account = get_db_result(sql)
        # Show the profile page with account info
        return render_template('test_heart.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/result', methods=['POST', 'GET'])
def result():
    age = int(request.form['age'])
    sex = int(request.form['sex'])
    trestbps = float(request.form['trestbps'])
    chol = float(request.form['chol'])
    restecg = float(request.form['restecg'])
    thalach = float(request.form['thalach'])
    exang = int(request.form['exang'])
    cp = int(request.form['cp'])
    fbs = float(request.form['fbs'])
    x = np.array([age, sex, cp, trestbps, chol, fbs, restecg,
                  thalach, exang]).reshape(1, -1)

    scaler_path = os.path.join(os.path.dirname(__file__), 'models/scaler.pkl')
    scaler = None
    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)

    x = scaler.transform(x)

    model_path = os.path.join(os.path.dirname(__file__), 'models/rfc.sav')
    clf = joblib.load(model_path)

    y = clf.predict(x)
    print(y)
    # No heart disease
    if y == 0:
        #return render_template('test_heart.html', msg='You have been diagnosed with no disease. Congratulations', line1='The algorithm has diagnosed you with no heart disease based on your inputs. However it might be better to talk to a doctor regardless.')
        return render_template('nodisease.html')
    # y=1,2,4,4 are stages of heart disease
    else:
        #msg='You have been diagnosed with Stage'+str(y)
        #return render_template('test_heart.html', msg=msg,line1='Heart disease can be classified into 4 stages(stage 1 to 4) based on severity of artery blockage. Artery blockage>50% indicates presence of heart disease. Higher the blockage, higher is the stage of heart disease. Stage 3 and 4 are called chronic heart disease and risk of heart attack at anyday in such patients in very high.')
        return render_template('heartdisease.html', stage=int(y))

if __name__ == '__main__':
   app.run(host='localhost', port=8080, debug=True)
