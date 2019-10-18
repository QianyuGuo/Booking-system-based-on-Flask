from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate, MigrateCommand
from flask_script import Shell, Manager
from flask_mail import Mail, Message
import os

from sqlalchemy.orm import backref

app = Flask(__name__)
app.config.update(
    DEBUG=True,
    MAIL_SERVER='smtp.qq.com',
    MAIL_PROT=25,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME='631332370@qq.com',
    MAIL_PASSWORD='uxdnmoihgpwvbeea',
    MAIL_DEBUG=True
)

mail = Mail(app)

manager = Manager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = "carwashing"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    subtitle = db.Column(db.String(50))
    author = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)

    def __repr__(self):
        return 'Blogpost:'.format(self.name)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(28))
    mail = db.Column(db.String(30))
    name = db.Column(db.String(60))
    work_phone = db.Column(db.String(20))
    home_phone = db.Column(db.String(20))
    car_information = db.Column(db.String(100))
    mobile_phone = db.Column(db.String(20))
    address = db.Column(db.String(100))
    apts = db.relationship('Appointment', backref = 'user')
    def __repr__(self):
        return 'User:'.format(self.name)


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    options = db.Column(db.String(50))
    apt_time = db.Column(db.String(30))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    car_type = db.Column(db.String(10))
    address = db.Column(db.String(100))
    requirement = db.Column(db.Text)

    def __repr__(self):
        return 'Appointment:'.format(self.name)

class Availible_times(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    times = db.Column(db.String(30))
    def __repr__(self):
        return 'Availible_times:'.format(self.name)

@app.route('/')
def index():
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()

    return render_template('index.html', posts=posts)


@app.route('/home/<int:user_id>', methods=['GET', 'POST'])
def home(user_id):
    user = User.query.get(user_id)
    return render_template('home.html', user=user)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/post/<int:post_id>')
def post(post_id):
    post = Blogpost.query.filter_by(id=post_id).one()

    return render_template('post.html', post=post)


@app.route('/sign')
def sign():
    return render_template('sign.html')


@app.route('/sign', methods=['POST'])
def signup():
    mail = request.form['mail']
    name = request.form['name']
    password = request.form['password']
    mobile_phone = request.form['mobile_phone']
    user = User.query.filter(User.mail == mail).first()
    if user:
        flash("User already exists, please login")
        return render_template('sign.html')
    elif all([mail, password, mobile_phone]):
        user = User(mail=mail, name=name, password=password, mobile_phone=mobile_phone)
        db.session.add(user)
        db.session.commit()
        return render_template('home.html', user=user)
    else:
        flash("The information is incomplete, please input again")
        return render_template('sign.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/log', methods=['GET', 'POST'])
def log():
    mail = request.form['mail']
    password = request.form['password']
    user = User.query.filter(User.mail == mail,
                             User.password == password).first()
    if user:
        if user.mail == "admin":

            return redirect(url_for('admin', user_id=user.id))
        else:
            return render_template('home.html', user=user)
    else:
        flash("E-mail address or password are incorrect, input again")
        return render_template('login.html')

@app.route('/admin/<int:user_id>', methods=['GET', 'POST'])
def admin(user_id):
    appointments = Appointment.query.all()
    user=User.query.get(user_id)
    return render_template('admin.html', appointments=appointments, user=user)


@app.route('/update/<int:user_id>', methods=['GET', 'POST'])
def update(user_id):
    user = User.query.get(user_id)
    name = request.form['name']
    if name:
        user.name = name
    mobile_phone = request.form['mobile_phone']
    if mobile_phone:
        user.mobile_phone = mobile_phone
    work_phone = request.form['work_phone']
    if work_phone:
        user.work_phone = work_phone
    home_phone = request.form['home_phone']
    if home_phone:
        user.home_phone = home_phone
    address = request.form['address']
    if address:
        user.address = address
    car_type = request.form['car_type']
    if car_type:
        user.car_information = car_type
    db.session.commit()
    return redirect(url_for('account', user_id=user.id))

@app.route('/history/<int:user_id>', methods=['POST', 'GET'])
def history(user_id):
    user = User.query.get(user_id)
    if user:
        appointments=Appointment.query.filter(Appointment.user_id==user_id)
        return render_template('appointments.html', user=user,appointments=appointments)
    else:
        return render_template('home.html', user=user)

@app.route('/account/<int:user_id>', methods=['POST', 'GET'])
def account(user_id):
    user = User.query.get(user_id)
    if user:
        appointments=Appointment.query.filter(Appointment.user_id==user_id)
        return render_template('account.html', user=user,appointments=appointments)
    else:
        return render_template('home.html', user=user)



@app.route('/booking/<int:user_id>', methods=['GET', 'POST'])
def booking(user_id):
    user = User.query.get(user_id)
    apt_times = Availible_times.query.order_by(Availible_times.times.desc()).all()
    # print(apt_times)
    return render_template('booking.html', user=user, apt_times=apt_times)


@app.route('/reservation/<int:user_id>', methods=['GET', 'POST'])
def reservation(user_id):
    user = User.query.get(user_id)
    car_type = request.form['cartype']
    apt_time = request.form['apt_time']
    options = request.form['sel_option']
    requirement = request.form['content']
    address = request.form['address']
    if all([car_type, apt_time, options]):
        if address:
            selected_time = Availible_times.query.get(apt_time)
            appointment = Appointment(car_type=car_type, apt_time=selected_time.times, options=options, requirement=requirement,
                                      user_id=user_id, address=address)
        else:
            selected_time = Availible_times.query.get(apt_time)
            appointment = Appointment(car_type=car_type, apt_time=selected_time.times, options=options, requirement=requirement,
                                      user_id=user_id, address=user.address)

        msg = Message("Booking successfully ", sender='631332370@qq.com', recipients=[user.mail])
        msg.body = "Booking successfully! " \
                   "Appointment details: " \
                   "Car type is %s. " \
                   "Appointment time is %s. " \
                   "Washing option is %s. " \
                   "Special requirement is %s. " \
                   "Appointment address is %s" % (
                       car_type, selected_time.times, options, requirement, appointment.address)
        mail.send(msg)

        db.session.add(appointment)
        db.session.delete(selected_time)
        db.session.commit()

        return redirect(url_for('home', user_id=user_id))

    else:
        flash("The information is incomplete, please input again")
        return redirect(url_for('booking', user_id=user_id))


@app.route('/deleteApt/<int:apt_id>', methods=['GET', 'POST'])
def deleteApt(apt_id):
    appointment = Appointment.query.get(apt_id)
    db.session.delete(appointment)
    db.session.commit()
    appointments = Appointment.query.all()
    user=User.query.get(1)
    return redirect(url_for('admin', user_id=user.id))

@app.route('/delete/<int:apt_id>', methods=['GET', 'POST'])
def delete(apt_id):
    appointment = Appointment.query.get(apt_id)
    user = User.query.get(appointment.user_id)
    msg = Message("Delete successfully ", sender='631332370@qq.com', recipients=[user.mail])
    msg.body = "Delete successfully!" \
               " Appointment details:" \
               " Car type is %s. " \
               "Appointment time is %s. " \
               "Washing option is %s. Special requirement is %s." \
               " Appointment address is %s" % (
                   appointment.car_type, appointment.apt_time, appointment.options, appointment.requirement,
                   appointment.address)
    mail.send(msg)
    db.session.delete(appointment)
    db.session.commit()
    appointments = Appointment.query.filter(Appointment.user_id == user.id)

    return redirect(url_for('history', user_id=user.id))

@app.route('/rebook/<int:apt_id>', methods=['GET', 'POST'])
def rebook(apt_id):
    appointment = Appointment.query.get(apt_id)
    user = User.query.get(appointment.user_id)
    db.session.delete(appointment)
    db.session.commit()
    return render_template('rebook.html', user=user)

@app.route('/rebooking/<int:user_id>', methods=['GET', 'POST'])
def rebooking(user_id):
    user = User.query.get(user_id)
    car_type = request.form['cartype']
    apt_time = request.form['apttime']
    options = request.form['sel_option']
    requirement = request.form['content']
    address = request.form['address']
    if all([car_type, apt_time, options]):
        apt=Appointment.query.filter(Appointment.apt_time==apt_time).all()
        if apt :
            flash("This time is unavailable, please select another one")
            return redirect(url_for('rebook', user_id=user_id))
        elif address:
            appointment = Appointment(car_type=car_type, apt_time=apt_time, options=options, requirement=requirement,
                                      user_id=user_id, address=address)
        else:
            appointment = Appointment(car_type=car_type, apt_time=apt_time, options=options, requirement=requirement,
                                      user_id=user_id, address=user.address)
        db.session.add(appointment)
        db.session.commit()

        msg = Message("Rebooking successfully ", sender='631332370@qq.com', recipients=[user.mail])
        msg.body = "Rebooking successfully! " \
                   "New appointment details: " \
                   "Car type is %s. " \
                   "Appointment time is %s. " \
                   "Washing option is %s. " \
                   "Special requirement is %s. " \
                   "Appointment address is %s" % (
                       car_type, apt_time, options, requirement, appointment.address)
        mail.send(msg)
        return redirect(url_for('home', user_id=user_id))

    else:
        flash("The information is incomplete, please input again")
        return redirect(url_for('rebook', user_id=user_id))


if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    admin = User(mail='admin', password='admin')
    user1 = User(mail='248172013@qq.com', password='1111', name='jack', mobile_phone='1234567890',address='111 Swanston St')
    appointment1 = Appointment(apt_time='2019/10/25 17:00', car_type='SUV', options='wash outside $15',
                               requirement='carefully',address='111 Swanston St', user_id='2')
    appointment2 = Appointment(apt_time='2019/10/25 19:00', car_type='Sedan', options='deluxe wash $30',
                               requirement='best', address='555 Swanston St', user_id='2')
    availible_times1 = Availible_times(times='2019/10/26 17:00')
    availible_times2 = Availible_times(times='2019/10/26 17:40')
    availible_times3 = Availible_times(times='2019/10/26 18:20')
    availible_times4 = Availible_times(times='2019/10/26 19:00')
    availible_times5 = Availible_times(times='2019/10/27 17:00')
    availible_times6 = Availible_times(times='2019/10/27 17:40')
    availible_times7 = Availible_times(times='2019/10/27 18:20')
    availible_times8 = Availible_times(times='2019/10/27 19:00')

    db.session.add_all([appointment1,appointment2,admin,user1,availible_times1,availible_times2,availible_times3,availible_times4,availible_times5,availible_times6,availible_times7,availible_times8])
    db.session.commit()
    app.run(debug=True)
    # app.run(host = '0.0.0.0' ,port = 5000, debug = 'True')
