from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate,MigrateCommand
from flask_script import Shell,Manager

app = Flask(__name__)
manager = Manager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key="carwashing"

db = SQLAlchemy(app)
migrate = Migrate(app,db)


manager.add_command('db',MigrateCommand)


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
    mobile_phone = db.Column(db.String(20))
    address = db.Column(db.String(100))
    def __repr__(self):
        return 'User:'.format(self.name)


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    day = db.Column(db.Integer)
    type = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    def __repr__(self):
        return 'Appointment:'.format(self.name)

@app.route('/')
def index():
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()

    return render_template('index.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Blogpost.query.filter_by(id=post_id).one()

    return render_template('post.html', post=post)

@app.route('/add')
def add():
    return render_template('add.html')
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
        return render_template('home.html', user=user)
    else:
        flash("E-mail address or password are incorrect, input again")
        return render_template('login.html')



@app.route('/update/<int:user_id>', methods=['GET','POST'])
def update(user_id):
    user = User.query.get(user_id)
    user.name = request.form['name']
    user.mobile_phone = request.form['mobile_phone']
    user.work_phone = request.form['work_phone']
    user.home_phone = request.form['home_phone']
    user.address = request.form['address']
    db.session.commit()
    return redirect(url_for('account',user_id=user.id))


@app.route('/account/<int:user_id>',methods=['POST','GET'])
def account(user_id):
    user=User.query.get(user_id)
    if user:
        return render_template('account.html',user=user)
    else:
        return render_template('home.html',user=user)





@app.route('/addpost', methods=['POST'])
def addpost():
    title = request.form['title']
    subtitle = request.form['subtitle']
    author = request.form['author']
    content = request.form['content']

    post = Blogpost(title=title, subtitle=subtitle, author=author, content=content, date_posted=datetime.now())

    db.session.add(post)
    db.session.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    # db.drop_all()
    # db.create_all()
    app.run(debug=True)