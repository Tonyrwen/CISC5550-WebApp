# This is a simple example web app that is meant to illustrate the basics.
from flask import Flask, render_template, redirect, g, request, url_for, jsonify, json
import urllib
import requests  # similar purpose to urllib.request, just more convenience
import os
from flask import Flask
from flask import render_template, url_for, g, flash, request, redirect, Response
import sqlite3
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from forms import LoginForm
import os, re

SECRET_KEY = os.urandom(32)
DATABASE = 'todolist.db'

app = Flask(__name__)
#TODO_API_URL = "http://"+os.environ['TODO_API_IP']+":5001"
TODO_API_URL = "http://127.0.0.1:5001"
app.config.from_object(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.debug=True

login_manager = LoginManager(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id, email, password):
         self.id = str(id)
         self.email = email
         self.password = password
         self.authenticated = False
    def is_active(self):
         return self.is_active()
    def is_anonymous(self):
         return False
    def is_authenticated(self):
         return self.authenticated
    def is_active(self):
         return True
    def get_id(self):
         return self.id
     
@login_manager.user_loader
def load_user(user_id):
   conn = get_db()
   curs = conn.cursor()
   curs.execute("SELECT * from login where user_id = (?)",[user_id])
   lu = curs.fetchone()
   if lu is None:
      return None
   else:
      return User(int(lu[0]), lu[1], lu[2])
  
@app.route("/login", methods=['GET','POST'])
def login():
  if current_user.is_authenticated:
     return redirect(url_for('profile'))
  form = LoginForm()
  if form.validate_on_submit():
     conn = get_db()
     curs = conn.cursor()
     curs.execute("SELECT * FROM login where email = (?)",    [form.email.data])
     user = list(curs.fetchone())
     Us = load_user(user[0])
     if form.email.data == Us.email and form.password.data == Us.password:
        login_user(Us, remember=form.remember.data)
        Umail = list({form.email.data})[0].split('@')[0]
        print(form.email.data)
        flash('Logged in successfully '+Umail)
        return redirect(url_for('show_list', email=urllib.parse.quote(form.email.data)))
     else:
        flash('Login Unsuccessfull.')
  return render_template('login.html',title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form :
        email = request.form['email']
        password = request.form['password']
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM login WHERE email="'+email+'"')
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not email or not password:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO login (email, password) VALUES ("'+email+'","'+password+'")')
            conn.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect(app.config['DATABASE'])
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route("/profile/<email>")
def show_list(email):
    email = urllib.parse.unquote(email)
    Umail = list({email})[0].split('@')[0]
    urlemail = urllib.parse.quote(email)
    resp = requests.get(TODO_API_URL+"/api/items/"+urlemail)
    resp = resp.json()
    return render_template('index.html', todolist=resp, user=Umail, email = email)


@app.route("/add", methods=['POST'])
def add_entry():
    requests.post(TODO_API_URL+"/api/items", json={
                  "useremail": request.form['email'],
                  "what_to_do": request.form['what_to_do'], "due_date": request.form['due_date']})
    return redirect(url_for('show_list', email = request.form['email']))


@app.route("/delete/<email>/<item>")
def delete_entry(email,item):
    #email, item = urllib.parse.quote(email), urllib.parse.quote(item)
    requests.delete(TODO_API_URL+"/api/items/"+email+"/"+item)
    return redirect(url_for('show_list', email = urllib.parse.unquote(email)))


@app.route("/mark/<email>/<item>")
def mark_as_done(email,item):
    #email, item = urllib.parse.quote(email), urllib.parse.quote(item)
    requests.put(TODO_API_URL+"/api/items/"+email+"/"+item)
    return redirect(url_for('show_list', email = urllib.parse.unquote(email)))


if __name__ == "__main__":
    app.run("0.0.0.0")
