from flask import Flask, render_template,request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, update, and_
from sqlalchemy.orm import Session
import psycopg2
from datetime import datetime
from sqlalchemy.sql.operators import nullsfirst_op

from datetime import datetime

app = Flask(__name__)

#connection to database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:abc123@localhost/postgres'
db=SQLAlchemy(app)
session =Session(db.engine)
conn=db.engine.connect()

# #tables
# City = db.Table('city', db.metadata, autoload=True, autoload_with=db.engine)
User = db.Table('users', db.metadata, autoload=True, autoload_with=db.engine)
# UsersLog = db.Table('userslog', db.metadata, autoload=True, autoload_with=db.engine)
# Conf = db.Table('conference', db.metadata, autoload=True, autoload_with=db.engine)
# ConfRole = db.Table('conferenceroles', db.metadata, autoload=True, autoload_with=db.engine)
# ConfUpdate = db.Table('conferenceupdates', db.metadata, autoload=True, autoload_with=db.engine)
# Submission = db.Table('submissions', db.metadata, autoload=True, autoload_with=db.engine)

@app.route('/', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    email= request.form['email']
    password= request.form['password']
    query= select([User.c.password]).where(User.c.email == email)
    db_password= conn.execute(query).fetchone()
    if(db_password != None and  password == db_password[0] ):
      return redirect(url_for('main'))
    else:
      error = 'Wrong password or email'
      return render_template('login.html', error=error)
  else:   
    return render_template('login.html')

@app.route('/main', methods=['GET'])
def main():
  #  if request.method == 'POST':
  #     if (request.form['form_type'] == 'user'):
  #        return handle_status_change(form = request.form, model = 'User')
  #     return handle_status_change(form = request.form, model = 'Conference')
  #  else:
  return render_template('main.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
  if request.method == 'POST':
    name=request.form['name']
    lastname=request.form['lastname']
    email=request.form['email']
    phone=request.form['phone']
    address=request.form['address']
    password=request.form['password']
    confirmpassword=request.form['confirmpassword']
    error=''
    if(password != confirmpassword):
      error = 'Passwords do not match!!' 
      
    if(error == ''):
      new_user= User.insert().values(
        name=name,
        lname=lastname,
        email=email,
        password=password,
        phone=phone,
        address=address
      )
      conn.execute(new_user)
      return redirect(url_for('login'))
    else:
      return render_template('signup.html')
  else:
    return render_template('signup.html')

if __name__ == '__main__':
   app.run(debug = True)
