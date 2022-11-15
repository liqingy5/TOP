from flask import Flask, render_template
from flask import url_for
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy

import os
import sys


WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else: 
    prefix = 'sqlite:////'

app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app = Flask(__name__)

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







@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
   app.run()