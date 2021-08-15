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
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:tdg123@localhost/teknolandin'
db=SQLAlchemy(app)
session =Session(db.engine)
conn=db.engine.connect()

user_id = -1

#tables
User = db.Table('users', db.metadata, autoload=True, autoload_with=db.engine)
Product = db.Table('products', db.metadata, autoload=True, autoload_with=db.engine)

@app.route('/', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    email= request.form['email']
    password= request.form['password']
    query= select([User.c.password]).where(User.c.email == email)
    db_password= conn.execute(query).fetchone()

    query= select([User.c.userid]).where(User.c.email == email)
    global user_id
    user_id = conn.execute(query).fetchone()[0]
    
    if(db_password != None and  password == db_password[0] ):
      return redirect(url_for('main'))
    else:
      error = 'Wrong password or email'
      return render_template('login.html', error=error)
  else:   
    return render_template('login.html')

@app.route('/main', methods=['GET'])
def main():
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

@app.route('/sell_product' , methods=['GET'])
def sell_product():
  query=select([Product]).where(Product.c.owner_id == user_id)
  sellable_products = conn.execute(query).fetchall()
  return render_template('sellProduct.html', products = sellable_products)

@app.route('/buy_product' , methods=['GET'])
def buy_product():
  query = select([Product]).where(Product.c.owner_id == user_id)
  sellable_products = conn.execute(query).fetchall()
  return render_template('buyProduct.html', products=sellable_products)

@app.route('/update_budget' , methods=['GET'])
def update_budget():
  return render_template('updateBudget.html')

@app.route('/update_user' , methods=['GET'])
def update_user():
  return render_template('updateUser.html')

@app.route('/update_product' , methods=['GET'])
def update_product():
  return render_template('updateProduct.html')

@app.route('/delete_product' , methods=['GET'])
def delete_product():
  return render_template('deleteProduct.html')

@app.route('/cart' , methods=['GET'])
def show_cart():
  return render_template('deleteProduct.html')

if __name__ == '__main__':
   app.run(debug = True)
