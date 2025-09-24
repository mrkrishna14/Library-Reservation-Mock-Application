from flask import Flask, render_template, url_for, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import sqlite3 as sql
import sys
#from apscheduler.scheduler import Scheduler
import atexit



app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_name = User.query.filter_by(
            username=username.data).first()
        if existing_user_name:
            raise ValidationError(
                "That username already exists. Please choose a different one")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

    

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard', username=form.username.data))
    return render_template('login.html', form=form)


@app.route('/dashboard/<username>', methods=['GET', 'POST'])
@login_required
def dashboard(username):
    
    conn = sql.connect('reserve.db')
    conn.execute('CREATE TABLE IF NOT EXISTS libres (username TEXT, roomnumber TEXT, library TEXT, timeslot TEXT, available TEXT)')
    conn.close()
    session['username'] = username
    return render_template('dashboard2.html', username=username)

@app.route('/reserve', methods=['GET', 'POST'])
@login_required
def confirm():
    user = session.get('username', None)
    # Debug print - remove in production
    print(user, file=sys.stderr)
    return render_template('reserve.html', user=user)



@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    con = sql.connect("reserve.db")
    con.row_factory = sql.Row
    cur = con.cursor()

    library = str(request.form.get('Library'))
    selected_time = str(request.form.get('Available Times'))

    roomlist = ['Room1', 'Room2', 'Room3', 'Room4']
    cur.execute("SELECT roomnumber FROM libres WHERE library=? and timeslot=?",
                [library, selected_time])

    rows = cur.fetchall()

    if cur.rowcount != 0:
        for row in rows:
            roomlist.remove(str(row[0]))
            # Debug print - remove in production
            print(row[0], file=sys.stderr)

    liblist = ['Dougherty Station Library', 'San Ramon Library']
    
    session['user_lib'] = library
    session['user_time'] = selected_time

    return render_template('avrooms.html', rl=roomlist, sel_lib=library, sel_time=selected_time, ll=liblist)




@app.route('/finalize', methods=['GET', 'POST'])
def finalize():
    sel_room = str(request.form.get('rooms'))
    user = session.get('username', None)
    sel_time = session.get('user_time', None)
    sel_lib = session.get('user_lib', None)
    con = sql.connect("reserve.db")
    con.row_factory = sql.Row
    c = con.cursor()

    c.execute("SELECT * from libres WHERE username=?", (user,))
    rows = c.fetchall()
    if not rows:
        c.execute("INSERT INTO libres (username, roomnumber, library, timeslot, available) VALUES (?,?,?,?,?)",
              (user, sel_room, sel_lib, sel_time, 'no'))

        con.commit()
        con.close()
        return render_template('finalize.html', user=user, selected_room=sel_room, selected_lib=sel_lib, selected_time=sel_time)
    else:
        flash("Sorry, our system shows that you already have made a reservation. You are not allowed to reserve more than one room per day.")
        return render_template('error.html', user=user, rows=rows)


@app.route('/view', methods=['GET'])
def view():
    if request.method == "GET":
        user = session.get('username', None)
        conn = sql.connect('reserve.db')
        conn.row_factory = sql.Row
        c = conn.cursor()
        c.execute("SELECT * FROM libres WHERE username=?", [user])
        rows = c.fetchall()
        return render_template("view.html", rows=rows, user=user)


@app.route('/cancel', methods=['GET', 'POST'])
def cancel():
    user = session.get('username', None)
    # Debug print - remove in production
    print(user, file=sys.stderr)
    conn = sql.connect("reserve.db")
    conn.row_factory = sql.Row
    c = conn.cursor()

    c.execute("DELETE FROM libres WHERE username=?", [user])

    conn.commit()
    return render_template("cancel.html", user=user)




@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form, user=user)


##cron = Scheduler(daemon=True)
# Explicitly kick off the background thread
#cron.start()

#@cron.interval_schedule(minute=1)
#def clear_database():
 #   conn = sql.connect("reserve.db")
  #  cur = conn.cursor()
   # cur.execute(
    #        "DELETE FROM libres")
    #conn.commit()
    #print("Deleted reservations")

# Shutdown your cron thread if the web process is stopped
#atexit.register(lambda: cron.shutdown(wait=False))


if __name__ == '__main__':
    # Set debug=False for production
    app.run(debug=True)
