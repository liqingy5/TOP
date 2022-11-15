from flask import Flask, render_template, request, redirect, url_for, session
from flask import url_for
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
import click


import os
import sys


WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else: 
    prefix = 'sqlite:////'
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# class User(db.Model): 
#     id = db.Column(db.Integer, primary_key=True) 
#     username = db.Column(db.String(20))  
#     password = db.Column(db.String(20))  
#     PetOwner = db.relationship('PetOwner', backref='user')

# class PetOwner(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(20))
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     pets = db.relationship('Pet', backref='PetOwner', lazy='dynamic')


# class Seniors(db.Model):  
#     id = db.Column(db.Integer, primary_key=True)  
#     name = db.Column(db.String(20)) 
#     ages = db.Column(db.Integer) 





@app.route('/login', methods =['POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
        # account = cursor.fetchone()
        if len(username) != 0 and len(password) != 0:
            # session['loggedin'] = True
            # session['id'] = account['id']
            # session['username'] = account['username']
            msg = 'Logged in successfully !'
            print(msg)
            return redirect(url_for('root'))
        else:
            msg = 'Incorrect username / password !'
    return render_template('/components/login.html')

@app.route('/scheduleRequest',methods=['POST'])
def scheduleRequest():
    # if request.method == 'POST':
    #     pet = request.form['pet']
    #     date = request.form['date']
    #     droptime = request.form['dropOffTime']
    #     picktime = request.form['pickUpTime']
    #     # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #     # cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s, % s)', (name, date, time, pet))
    #     # mysql.connection.commit()
    #     return redirect(url_for('index'))
    return render_template('/components/schedule.html')


    
@app.route('/UserinfoUpdate',methods=['POST'])
def UserinfoUpdate():
    # if request.method == 'POST':
    #     name = request.form['name']
    #     date = request.form['date']
    #     time = request.form['time']
    #     pet = request.form['pet']
    #     # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #     # cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s, % s)', (name, date, time, pet))
    #     # mysql.connection.commit()
    #     return redirect(url_for('index'))
    return render_template('/components/info.html')

@app.route('/petInfoUpdate',methods=['POST'])
def petInfoUpdate():
    # if request.method == 'POST':
    #     name = request.form['name']
    #     date = request.form['date']
    #     time = request.form['time']
    #     pet = request.form['pet']
    #     # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #     # cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s, % s)', (name, date, time, pet))
    #     # mysql.connection.commit()
    #     return redirect(url_for('index'))
    return render_template('/components/pet.html')


    
@app.route('/viewPet',methods=['GET'])
def viewPet():
    # if request.method == 'POST':
    #     name = request.form['name']
    #     date = request.form['date']
    #     time = request.form['time']
    #     pet = request.form['pet']
    #     # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #     # cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s, % s)', (name, date, time, pet))
    #     # mysql.connection.commit()
    #     return redirect(url_for('index'))
    return render_template('/components/petsList.html')


@app.route('/')
def index():
    return render_template('/components/login.html')
@app.route('/index')
def root():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('/components/home.html')

@app.route('/schedule')
def schedule():
    return render_template('/components/schedule.html')

@app.route('/myInfo')
def myInfo():
    return render_template('/components/info.html')
    
pets=[{'Owner':'Aaron Wu','Pet':'Cat','Name':'Dobby','Breed':'Abyssinian','Age':'6 months','Weight':'7 lbs','Activity_level':'annoying','food_preference':'raw meat'},
{'Owner':'Aaron Wu','Pet':'Cat','Name':'Yoda','Breed':'Russian Blue','Age':'18 months','Weight':'10 lbs','Activity_level':'quiet','food_preference':'raw meat'}
]
@app.route('/petsList/view/<pet_name>',methods=['GET'])
def view(pet_name):
    for pet in pets:
        if pet['Name']==pet_name:
            return render_template('/components/pet.html',pet=pet)
    return render_template('/components/petsList.html')


@app.route('/pet')
def pet():
    return render_template('/components/pet.html')

@app.route('/petsList')
def petsList():
    return render_template('/components/petsList.html',pets=pets)

if __name__ == '__main__':
   app.run()