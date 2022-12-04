from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask import url_for
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_required, logout_user, login_user, current_user
from datetime import datetime, timedelta
import random


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
    type = db.Column(db.Integer)
    breed = db.Column(db.String(20))
    age = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    activity_level = db.Column(db.Integer)
    food_preference = db.Column(db.String(40))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Senior(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer)
    fav_type = db.Column(db.PickleType)
    fav_activity = db.Column(db.Integer)
    weekday=db.Column(db.PickleType)
    time_from = db.Column(db.DateTime)
    time_to = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
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
    pet1 = Pet(name='Dobby', type=4, breed='Abyssinian', age=6, weight=7,
               activity_level=1, food_preference='raw meat', user=user)
    pet2 = Pet(name='Yoda', type=4, breed='Russian Blue', age=18, weight=10,
               activity_level=3, food_preference='raw meat', user=user)
    
    today = datetime.today().strftime('%Y-%m-%d')
    today = datetime.strptime(today, '%Y-%m-%d')
    weeks1 = [today+timedelta(days=i) for i in range(5, 8)]
    time_from_1 = datetime.strptime('10:00', '%H:%M')
    time_to_1 = datetime.strptime('12:00', '%H:%M')
    weeks2 = [today+timedelta(days=i) for i in range(3, 6)]
    time_from_2 = datetime.strptime('10:00', '%H:%M')
    time_to_2 = datetime.strptime('15:00', '%H:%M')
    
    senior1 = Senior(age=50, fav_type=[1,2,4],
                     fav_activity=1, weekday=weeks1,time_from=time_from_1,time_to=time_to_1, user=user1)
    senior2 = Senior(age=66, fav_type=[4], fav_activity=3,weekday=weeks2,
                     time_from=time_from_2,time_to=time_to_2, user=user2)
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
            flash('Invalid input.','error')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()
        if user and username == user.username and user.validate_password(password):
            login_user(user)
            flash('Login success.','success')
            return redirect(url_for('index'))
        flash('Invalid username or password.','error')
        return redirect(url_for('login'))
    return render_template('/components/login.html')


@app.route('/logout')
@login_required  # 用于视图保护
def logout():
    logout_user()  # 登出用户
    flash('Goodbye.','success')
    return redirect(url_for('login'))  # 重定向回首页

def generate_senior_list(seniors, pet, droptime, picktime):
    ret = []
    required_date = droptime.strftime("%Y-%m-%d")
    droptime = droptime.strftime("%H:%M:%S")
    picktime = picktime.strftime("%H:%M:%S")
    for senior in seniors:

        if pet.type not in senior.fav_type:
            continue
        if pet.activity_level != senior.fav_activity:
            continue
        found = False

        for date in senior.weekday:
            if date.strftime("%Y-%m-%d") == required_date:
                found = True
                break
        if not found:
            continue

        time_from = senior.time_from.strftime("%H:%M:%S")
        time_to = senior.time_to.strftime("%H:%M:%S")
        if droptime<time_from or picktime>time_to:
            continue

        ret.append(senior)

    return ret

def get_all_users(seniors):
    ret = []
    for senior in seniors:
        ret.append(User.query.get(senior.user_id))

    return ret

@app.route('/AI_schedule')
def AI_schedule():
    pet_id = request.args['pet_id']
    pet = Pet.query.get(pet_id)
    droptime = datetime.strptime(request.args['droptime'], "%Y-%m-%d %H:%M:%S")
    picktime = datetime.strptime(request.args['picktime'], "%Y-%m-%d %H:%M:%S")
    seniors = Senior.query.all()
    seniors_aval = generate_senior_list(seniors, pet, droptime, picktime)
    users = get_all_users(seniors_aval)
    if len(seniors_aval)>=1:
        seniors_aval = seniors_aval[0:1]
        users = users[0:1]
    return render_template('/components/AI_schedule.html',
                           seniors=seniors_aval,
                           users=users,
                           pet_id=pet_id,
                           droptime=droptime,
                           picktime=picktime,
                           )

@app.route('/hybrid_schedule')
def hybrid_schedule():
    pet_id = request.args['pet_id']
    pet = Pet.query.get(pet_id)
    droptime = datetime.strptime(request.args['droptime'], "%Y-%m-%d %H:%M:%S")
    picktime = datetime.strptime(request.args['picktime'], "%Y-%m-%d %H:%M:%S")
    seniors = Senior.query.all()
    seniors_aval = generate_senior_list(seniors, pet, droptime, picktime)
    users = get_all_users(seniors_aval)
    if len(seniors_aval)>=5:
        seniors_aval = seniors_aval[0:5]
        users = users[0:5]
    return render_template('/components/hybrid_schedule.html',
                           seniors=seniors_aval,
                           users=users,
                           pet_id=pet_id,
                           droptime=droptime,
                           picktime=picktime,
                           )


@app.route('/manual_schedule')
def manual_schedule():
    pet_id = request.args['pet_id']
    pet = Pet.query.get(pet_id)
    droptime = datetime.strptime(request.args['droptime'], "%Y-%m-%d %H:%M:%S")
    picktime = datetime.strptime(request.args['picktime'], "%Y-%m-%d %H:%M:%S")
    seniors = Senior.query.all()
    seniors_aval = generate_senior_list(seniors, pet, droptime, picktime)
    users = get_all_users(seniors_aval)
    return render_template('/components/manual_schedule.html',
                           seniors=seniors_aval,
                           users=users,
                           pet_id=pet_id,
                           droptime=droptime,
                           picktime=picktime,
                           )


@app.route('/confirm', methods=['POST'])
def confirm():
    date = datetime.strptime(request.form['droptime'].split()[0], "%Y-%m-%d")
    dropOff = datetime.strptime(request.form['droptime'].split()[1], "%H:%M:%S")
    pickUp = datetime.strptime(request.form['picktime'].split()[1], "%H:%M:%S")
    pet_id = request.form['pet_id']
    senior_id = request.form['senior_id']
    schedule = Schedule(date=date,
                        dropOff=dropOff,
                        pickUp=pickUp,
                        pet_id=pet_id,
                        senior_id=senior_id,
                        user_id=current_user.id)
    db.session.add(schedule)
    db.session.commit()
    return render_template('/components/confirm.html')


@app.route('/index')
@login_required
def index():
    return render_template('index.html')


@app.route('/home')
@login_required
def home():
    return render_template('/components/home.html')


@app.route('/schedule', methods=['GET', 'POST'])
@login_required
def schedule():
    today = datetime.today().date()
    choosebleDate = [today + timedelta(days=i) for i in range(1,8)]
    if request.method == 'POST':
        pet_id = int(request.form['pet'])
        date = request.form['weekdaysSelect']
        droptime = request.form['dropOffTime']
        picktime = request.form['pickUpTime']
        print(date)
        # print('INSERT INTO accounts VALUES (NULL, % s, % s, % s, % s)',
        #       (pet, date, droptime, picktime))
        # print(request.form['submitBtn'])

        print(datetime.strptime('12:00', '%H:%M'))
        if(pet_id==-1):
            flash("You don't have any pet!",'error')
            return redirect(url_for('schedule'))
        
        if date == '' or droptime == '' or picktime == '':
            flash('Invalid date or time.','error')
            return redirect('schedule')

        if picktime <= droptime:
            flash('Pick-up time cannot be earlier than drop-off time','error')
            return redirect('schedule')

        droptime = datetime.strptime(date + " " + droptime, "%Y-%m-%d %H:%M")
        picktime = datetime.strptime(date + " " + picktime, "%Y-%m-%d %H:%M")

        if droptime < datetime.now():
            flash('Drop-off time has to be in the future','error')
            return redirect('schedule')

        if picktime < datetime.now():
            flash('Pick-up time has to be in the future','error')
            return redirect('schedule')

        if request.form['submitBtn'] == "The most suitable senior citizen":
            print("Pet owner chooses to match the most suitable senior")
            return redirect(url_for('AI_schedule', pet_id=pet_id, droptime=droptime, picktime=picktime))
        elif request.form['submitBtn'] == "I'll choose from the top-5 subitable senior citizens":
            print("Pet owner chooses to select from the top 5 seniors")
            return redirect(url_for('hybrid_schedule', pet_id=pet_id, droptime=droptime, picktime=picktime))
        else:
            print("Pet owner chooses to manual select senior for pet")
            return redirect(url_for('manual_schedule', pet_id=pet_id, droptime=droptime, picktime=picktime))
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s, % s)', (name, date, time, pet))
        # mysql.connection.commit()
    pets = User.query.get(current_user.id).pets
    return render_template('/components/schedule.html', pets=pets,choosebleDate = choosebleDate)



@app.route('/myInfo', methods=['GET', 'POST'])
@login_required
def myInfo():
    user = User.query.get(current_user.id)
    if(request.method == 'POST'):
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        if not name or not phone or not address:
            flash('Invalid input.','error')
            return redirect(url_for('myInfo'))
        user.name = name
        user.phone = phone
        user.address = address
        db.session.commit()
        flash('Update success.','success')
    return render_template('/components/info.html', user=user)


@app.route('/sessions', methods=['GET', 'POST'])
@login_required
def sessions():
    # sessions = [[1,"Dobby","Elon Mask",datetime.strptime("2022-12-05", '%Y-%m-%d'),datetime.strptime('10:00', '%H:%M'),datetime.strptime('16:00', '%H:%M')],
    # [2,"Yoda","Brad Pitt",datetime.strptime("2022-12-02", '%Y-%m-%d'),datetime.strptime('10:00', '%H:%M'),datetime.strptime('16:00', '%H:%M')],
    # [3,"Yoda","Brad Pitt",datetime.strptime("2022-12-03", '%Y-%m-%d'),datetime.strptime('10:00', '%H:%M'),datetime.strptime('20:00', '%H:%M')]]
    # sessions.sort(key=lambda x: (x[3],x[5]),reverse=True)

    sessions = Schedule.query.filter_by(user_id=current_user.id).all()
    for session in sessions:
        senior_user_id = Senior.query.get(session.senior_id).user_id
        session.senior = User.query.get(senior_user_id).name
        session.pet = Pet.query.get(session.pet_id).name
    return render_template('/components/sessions.html',sessions = sessions,todayDate = datetime.today().date(),todayTime = datetime.today().time())

@app.route('/sessionDelete/<int:sessionID>')
@login_required
def sessionDelete(sessionID):
    session = Schedule.query.get(sessionID)
    db.session.delete(session)
    db.session.commit()
    flash('Delete success.','success')
    return redirect(url_for('sessions'))



@app.route('/seniorPref', methods=['GET', 'POST'])
@login_required
def seniorPref():
    senior = User.query.get(current_user.id).senior
    today = datetime.today().date()
    choosebleDate = [today + timedelta(days=i) for i in range(1,8)]
    seniorAvaliability=[]
    seniorTimeFrom = None
    seniorTimeTo = None
    if senior:
        seniorAvaliability = [x.date() for x in senior.weekday]
        seniorTimeFrom = senior.time_from.strftime('%H:%M')
        seniorTimeTo = senior.time_to.strftime('%H:%M')

    if(request.method == 'POST'):
        age = request.form['seniorAge']
        fav_type = request.form.getlist('typeSelect')
        fav_type = [eval(i) for i in fav_type]
        fav_activity = request.form['petActivity']
        weekday = request.form.getlist('weekdaysSelect')
        weekday = [datetime.strptime(i,'%Y-%m-%d') for i in weekday]
        time_from = request.form['from']
        time_from = datetime.strptime(time_from, '%H:%M')
        time_to = request.form['to']
        time_to = datetime.strptime(time_to, '%H:%M')
        if not age or not fav_type or not fav_activity or not weekday or not time_from or not time_to:
            flash('Invalid input.','error')
            return redirect(url_for('seniorPref'))
        
        if not senior:
            senior = Senior()
            senior.user_id = current_user.id

        senior.age = age
        senior.fav_type = fav_type
        senior.fav_activity = fav_activity
        senior.weekday = weekday
        senior.time_from = time_from
        senior.time_to = time_to

        db.session.add(senior)
        db.session.commit()
        flash('Preference Update success.','success')
        seniorAvaliability = [x.date() for x in senior.weekday]
        seniorTimeFrom = senior.time_from.strftime('%H:%M')
        seniorTimeTo = senior.time_to.strftime('%H:%M')
    return render_template('/components/seniorPrefer.html', senior=senior,choosebleDate = choosebleDate,seniorAvaliability = seniorAvaliability,time_from=seniorTimeFrom,time_to=seniorTimeTo)


@app.route('/petsList/delete/<int:pet_id>', methods=['GET', 'POST'])
@login_required
def deletePet(pet_id):
    pet = Pet.query.get(pet_id)
    db.session.delete(pet)
    db.session.commit()
    flash('Delete success.','success')
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
            flash('Invalid input.','error')
            return redirect(url_for('newPet'))
        pet = Pet(name=name, type=type, breed=breed, age=age, weight=weight,
                  activity_level=activity_level, food_preference=food_preference, user=current_user)
        db.session.add(pet)
        db.session.commit()
        flash('Add success.','success')
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
            flash('Invalid input.','error')
            return redirect(url_for('pet', pet_id=pet_id))

        pet.name = name
        pet.type = type
        pet.breed = breed
        pet.age = age
        pet.weight = weight
        pet.activity_level = activity_level
        pet.food_preference = food_preference
        db.session.commit()
        flash('Pet info Updated.','success')
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
    app.run(port=8000, debug=True)

