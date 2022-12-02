from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask import url_for
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_required, logout_user, login_user, current_user
from datetime import datetime, timedelta

import click


import os
import sys


WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = prefix + \
    os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev'

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(20))
    pets = db.relationship('Pet', backref='user')
    senior = db.relationship('Senior', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    type = db.Column(db.String(20))
    breed = db.Column(db.String(20))
    age = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    activity_level = db.Column(db.Integer)
    food_preference = db.Column(db.String(40))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Senior(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer)
    fav_type = db.Column(db.String(20))
    fav_activity = db.Column(db.Integer)
    time = db.Column(db.PickleType)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weekday = db.Column(db.Integer)
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
    user = User(username='1234', name='Aaron Wu',
                phone='(412)123-1234', address='sennot square')
    user1 = User(username='5678', name='Elon Mask',
                 phone='(123)456-7899', address='Twitter HQ')
    user2 = User(username='1357', name='Brad Pitt',
                 phone='(789)123-4566', address='California')
    user.set_password('1234')
    user1.set_password('5678')
    user2.set_password('1357')
    pet1 = Pet(name='Dobby', type='Cat', breed='Abyssinian', age=6, weight=7,
               activity_level=1, food_preference='raw meat', user=user)
    pet2 = Pet(name='Yoda', type='Cat', breed='Russian Blue', age=18, weight=10,
               activity_level=3, food_preference='raw meat', user=user)
    time1 = {1: [datetime.now().time(), (datetime.now() +
                                         timedelta(hours=5)).time()]}
    time2 = {2: [(datetime.now() -
                  timedelta(hours=1)).time(), (datetime.now() +
                                               timedelta(hours=3)).time()]}
    senior1 = Senior(age=50, fav_type="1,2,4,",
                     fav_activity=1, time=time1, user=user1)
    senior2 = Senior(age=66, fav_type="4", fav_activity=3,
                     time=time2, user=user2)
    db.session.add(user)
    db.session.add(pet1)
    db.session.add(pet2)
    db.session.add(senior1)
    db.session.add(senior2)
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


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()
        if user and username == user.username and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('index'))
        flash('Invalid username or password.')
        return redirect(url_for('login'))
    return render_template('/components/login.html')


@app.route('/logout')
@login_required  # 用于视图保护
def logout():
    logout_user()  # 登出用户
    flash('Goodbye.')
    return redirect(url_for('login'))  # 重定向回首页


@app.route('/scheduleRequest', methods=['GET', 'POST'])
def scheduleRequest():
    if request.method == 'POST':
        pet = request.form['pet']
        date = request.form['date']
        droptime = request.form['dropOffTime']
        picktime = request.form['pickUpTime']
        print('INSERT INTO accounts VALUES (NULL, % s, % s, % s, % s)',
              (pet, date, droptime, picktime))
        print(request.form['submitBtn'])
        if request.form['submitBtn'] == "The most suitable senior citizen":
            print("Pet owner chooses to match the most suitable senior")
            return redirect('AI_schedule')
        elif request.form['submitBtn'] == "I'll choose from the top-5 subitable senior citizens":
            print("Pet owner chooses to select from the top 5 seniors")
            return redirect('hybrid_schedule')
        else:
            print("Pet owner chooses to manual select senior for pet")
            return redirect('manual_schedule')
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s, % s)', (name, date, time, pet))
        # mysql.connection.commit()
        return redirect('scheduleRequest')
    return render_template('/components/schedule.html')


@app.route('/AI_schedule')
def AI_schedule():
    return render_template('/components/AI_schedule.html')


@app.route('/hybrid_schedule')
def hybrid_schedule():
    return render_template('/components/hybrid_schedule.html')


@app.route('/manual_schedule')
def manual_schedule():
    return render_template('/components/manual_schedule.html')


@app.route('/confirm')
def confirm():
    return render_template('/components/confirm.html')


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


@app.route('/myInfo', methods=['GET', 'POST'])
@login_required
def myInfo():
    user = User.query.get(current_user.id)
    if(request.method == 'POST'):
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        if not name or not phone or not address:
            flash('Invalid input.')
            return redirect(url_for('myInfo'))
        user.name = name
        user.phone = phone
        user.address = address
        db.session.commit()
        flash('Update success.')
    return render_template('/components/info.html', user=user)


@app.route('/petsList/delete/<int:pet_id>', methods=['GET', 'POST'])
@login_required
def deletePet(pet_id):
    pet = Pet.query.get(pet_id)
    db.session.delete(pet)
    db.session.commit()
    flash('Delete success.')
    return redirect(url_for('petsList'))


@app.route('/petsList/addPet', methods=['GET', 'POST'])
@login_required
def newPet():
    if(request.method == 'POST'):
        name = request.form['petName']
        type = request.form['petType']
        breed = request.form['petBreed']
        age = request.form['petAge']
        weight = request.form['petWeight']
        activity_level = request.form['petActivity']
        food_preference = request.form['petFoodPreference']
        if not name or not type or not breed or not age or not weight or not activity_level or not food_preference:
            flash('Invalid input.')
            return redirect(url_for('newPet'))
        pet = Pet(name=name, type=type, breed=breed, age=age, weight=weight,
                  activity_level=activity_level, food_preference=food_preference, user=current_user)
        db.session.add(pet)
        db.session.commit()
        flash('Add success.')
        return redirect(url_for('petsList'))
    return render_template('/components/pet.html', owner=current_user.name)


@app.route('/petsList/pet/<pet_id>', methods=['GET', 'POST'])
@login_required
def pet(pet_id):
    pet = Pet.query.get(pet_id)

    if request.method == 'POST':
        name = request.form['petName']
        type = request.form['petType']
        breed = request.form['petBreed']
        age = request.form['petAge']
        weight = request.form['petWeight']
        activity_level = request.form['petActivity']
        food_preference = request.form['petFoodPreference']
        if not name or not type or not breed or not age or not weight or not activity_level or not food_preference:
            flash('Invalid input.')
            return redirect(url_for('pet', pet_id=pet_id))

        pet.name = name
        pet.type = type
        pet.breed = breed
        pet.age = age
        pet.weight = weight
        pet.activity_level = activity_level
        pet.food_preference = food_preference
        db.session.commit()
        flash('Pet info Updated.')
        return redirect(url_for('petsList'))
    return render_template('/components/pet.html', pet=pet, owner=current_user.name)

# @app.route('/pet')
# def pet():
#     return render_template('/components/pet.html')


@app.route('/petsList')
@login_required
def petsList():
    pets = User.query.get(current_user.id).pets
    return render_template('/components/petsList.html', pets=pets)


if __name__ == '__main__':
    app.run()
