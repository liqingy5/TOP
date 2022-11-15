from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask import url_for
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager,UserMixin,login_required, logout_user, login_user


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
app.config['SECRET_KEY'] = 'dev'

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'



import click

class User(db.Model,UserMixin): 
    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))  
    name=db.Column(db.String(20))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(20))
    pets = db.relationship('Pet', backref='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    type= db.Column(db.String(20))
    breed = db.Column(db.String(20))
    age = db.Column(db.String(20))
    weight = db.Column(db.String(20))
    activity_level= db.Column(db.String(40))
    food_preference= db.Column(db.String(40))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))



class Senior(db.Model):  
    id = db.Column(db.Integer, primary_key=True)  
    name = db.Column(db.String(20)) 
    age = db.Column(db.Integer) 
    fav_type = db.Column(db.String(20))
    fav_breed = db.Column(db.String(20))
    fav_activity = db.Column(db.String(20))
    fav_age = db.Column(db.String(20))
    fav_weight = db.Column(db.String(20))

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20))
    dropOff = db.Column(db.DateTime)
    pickUp = db.Column(db.DateTime)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'))
    senior_id = db.Column(db.Integer, db.ForeignKey('senior.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user


@app.cli.command()
def forge():
    user = User(username='1234',name='Aaron Wu',phone='(412)123-1234',address='sennot square')
    user.set_password('1234')
    pet1 = Pet(name='Dobby',type='Cat',breed='Abyssinian',age='6 months',weight='7 lbs',activity_level='annoying',food_preference='raw meat',user=user)
    pet2 = Pet(name='Yoda',type='Cat',breed='Russian Blue',age='18 months',weight='10 lbs',activity_level='quiet',food_preference='raw meat',user=user)
    db.session.add(user)
    db.session.add(pet1)
    db.session.add(pet2)
    db.session.commit()
    click.echo('Done.')


@app.cli.command()  # 注册为命令，可以传入 name 参数来自定义命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息

@app.route('/')
@app.route('/login', methods =['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            return redirect(url_for('login'))
        user = User.query.filter_by(username=username).first()
        if username ==user.username and user.validate_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password.')
        return redirect(url_for('login'))
    return render_template('/components/login.html')

@app.route('/logout')
@login_required  # 用于视图保护，后面会详细介绍
def logout():
    logout_user()  # 登出用户
    return redirect(url_for('login'))  # 重定向回首页

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

# @app.route('/petInfoUpdate/<string:petName>',methods=['GET', 'POST'])
# def petInfoUpdate():
#     pet = Pet.query.get(petName)
#     if request.method == 'POST':
#         name = request.form['petName']
#         breed= request.form['petBreed']
#         age = request.form['petAge']
#         weight = request.form['petWeight']
#         activity_level= request.form['petActivity']
#         food_preference= request.form['petFoodPreference']
#         if not name or not breed or not age or not weight or not activity_level or not food_preference:
#             flash('Invalid input.')
#             return redirect(url_for('view', pet_name=petName))

#         pet.name = name
#         pet.breed = breed
#         pet.age = age
#         pet.weight = weight
#         pet.activity_level = activity_level
#         pet.food_preference = food_preference
#         db.session.commit()
#         flash('Pet info updated.')
#         return redirect(url_for('petsList'))
#     return render_template('/components/pet.html',pet=pet)


    
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


# @app.route('/')
# def index():
#     return render_template('/components/login.html')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/home')
@login_required
def home():
    return render_template('/components/home.html')

@app.route('/schedule')
@login_required
def schedule():
    return render_template('/components/schedule.html')

@app.route('/myInfo')
@login_required
def myInfo():
    return render_template('/components/info.html')
    
# pets=[{'Owner':'Aaron Wu','Pet':'Cat','Name':'Dobby','Breed':'Abyssinian','Age':'6 months','Weight':'7 lbs','Activity_level':'annoying','food_preference':'raw meat'},
# {'Owner':'Aaron Wu','Pet':'Cat','Name':'Yoda','Breed':'Russian Blue','Age':'18 months','Weight':'10 lbs','Activity_level':'quiet','food_preference':'raw meat'}
# ]
@app.route('/petsList/pet/<pet_id>',methods=['GET','POST'])
@login_required
def pet(pet_id):
    pet = Pet.query.get(pet_id)
    owner = User.query.get(pet.owner_id)
    
    if request.method =='POST':
        name = request.form['petName']
        breed= request.form['petBreed']
        age = request.form['petAge']
        weight = request.form['petWeight']
        activity_level= request.form['petActivity']
        food_preference= request.form['petFoodPreference']
        if not name or not breed or not age or not weight or not activity_level or not food_preference:
            return redirect(url_for('pet', pet_id=pet_id))

        pet.name = name
        pet.breed = breed
        pet.age = age
        pet.weight = weight
        pet.activity_level = activity_level
        pet.food_preference = food_preference
        db.session.commit()
        return redirect(url_for('petsList'))
    return render_template('/components/pet.html',pet=pet,owner=owner)

# @app.route('/pet')
# def pet():
#     return render_template('/components/pet.html')

@app.route('/petsList')
@login_required
def petsList():
    pets = Pet.query.all()
    print(pets)
    return render_template('/components/petsList.html',pets=pets)

if __name__ == '__main__':
   app.run()