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






# @app.route('/')
# @app.route('/login', methods =['GET', 'POST'])
# def login():
#     msg = ''
#     if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
#         username = request.form['username']
#         password = request.form['password']
#         # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         # cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
#         # account = cursor.fetchone()
#         if len(username) != 0 and len(password) != 0:
#             # session['loggedin'] = True
#             # session['id'] = account['id']
#             # session['username'] = account['username']
#             msg = 'Logged in successfully !'
#             return redirect(url_for('index'))
#         else:
#             msg = 'Incorrect username / password !'
#     return render_template('/components/login.html')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
   app.run()