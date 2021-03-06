from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, update, and_, func, desc
from sqlalchemy.orm import Session
import psycopg2
from datetime import datetime
from sqlalchemy.sql.operators import nullsfirst_op

from datetime import datetime

app = Flask(__name__)

# connection to database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:abc123@localhost/postgres'
db = SQLAlchemy(app)
session = Session(db.engine)
conn = db.engine.connect()

cart = {}
user_id = -1

# tables
User = db.Table('users', db.metadata, autoload=True, autoload_with=db.engine)
Product = db.Table('products', db.metadata, autoload=True, autoload_with=db.engine)
Product_sold = db.Table('product_sold', db.metadata, autoload=True, autoload_with=db.engine)


def getUser(user_id):
    query = select([User]).where(User.c.userid == user_id)
    executed = conn.execute(query).fetchall()
    user = executed[0]
    return user


def define_cart(user_id):
    product_list = list()
    temp_cart = {user_id: product_list}

    list_of_globals = globals()
    list_of_globals['cart'] = temp_cart


def get_list_from_user(user):
    global cart
    return cart[user];


def calculate_cart(user):
    user_list = cart[user]
    total_price = 0

    for prod in user_list:
        prod_price = prod.price - (prod.price * prod.salePercentage / 100)
        total_price = total_price + prod_price

    return total_price


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        query = select([User.c.password]).where(User.c.email == email)
        db_password = conn.execute(query).fetchone()

        query = select([User.c.userid]).where(User.c.email == email)
        global user_id
        user_id = conn.execute(query).fetchone()[0]

        if (db_password != None and password == db_password[0]):
            define_cart(user_id)
            return redirect(url_for('main'))
        else:
            error = 'Wrong password or email'
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')


@app.route('/main', methods=['GET', 'POST'])
def main():
  if (request.method == 'POST'):
    qq = request.form['sql_query']
    res = []
    err = ''
    try:
      res = conn.execute(qq).fetchall()
    except:
      err = 'There is error with the given query.'
    return render_template('main.html', user_id = user_id, sql_result = res, error = err)
  
  return render_template('main.html', user_id = user_id)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
  if request.method == 'POST':
    name = request.form['name']
    lastname = request.form['lastname']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']
    password = request.form['password']
    confirmpassword = request.form['confirmpassword']
    error = ''
    if (password != confirmpassword):
      error = 'Passwords do not match!!' 

    if(error == ''):
      new_user = User.insert().values(
        name = name,
        lname = lastname,
        email = email,
        password = password,
        phone = phone,
        address = address
      )
      conn.execute(new_user)
      return redirect(url_for('login'))
    else:
      return render_template('signup.html', user = {})

  return render_template('signup.html', user = {})

@app.route('/logout_user', methods=['GET'])
def logout_user():
  global user_id
  user_id = -1
  return redirect(url_for('login'))

@app.route('/sell_product', methods=['GET'])
def sell_product():
    query = select([Product]).where(Product.c.owner_id == user_id)
    sellable_products = conn.execute(query).fetchall()
    return render_template('sellProduct.html', products=sellable_products)


@app.route('/buy_product', methods=['GET'])
def buy_product():
    query = select([Product]).where(Product.c.owner_id != user_id)
    sellable_products = conn.execute(query).fetchall()
    return render_template('buyProduct.html', products=sellable_products, user_id=user_id)


@app.route('/update_budget', methods=['POST', 'GET'])
def update_budget():
    if request.method == 'POST':
        cardNumber = request.form['card-number']  # It is a dummy data
        budget = request.form['budget']

        query = update(User).where(User.c.userid == user_id).values(budget=User.c.budget + budget)
        conn.execute(query)
        query = select([User]).where(User.c.userid == user_id)
        user = conn.execute(query).first()
        return render_template('updateBudgetResult.html', budget=user.budget)
    else:
        return render_template('updateBudget.html')


@app.route('/update_user', methods=['GET', 'POST'])
def update_user():
  query = select([User]).where(User.c.userid == user_id)
  current_user = conn.execute(query).fetchone()
  if request.method == 'POST':
    name = request.form['name']
    lastname = request.form['lastname']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']
    password = request.form['password']
    confirmpassword = request.form['confirmpassword']
    error = ''
    if (password != confirmpassword):
      error = 'Passwords do not match!!' 

    if(error == ''):
      new_user = User.update().where(User.c.userid == user_id).values(
        name = name,
        lname = lastname,
        email = email,
        password = password,
        phone = phone,
        address = address
      )
      conn.execute(new_user)
      return redirect(url_for('main'))
    
    return redirect(url_for('update_user'))

  return render_template('signup.html', user = current_user)


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        sname = request.form['shortname']
        category = request.form['category']
        publish_date = request.form['publish_date']
        price = request.form['price']
        stock = request.form['stock']

        owner_id = user_id
        query = Product.insert().values(
            owner_id=owner_id,
            name=name,
            shortname=sname,
            category=category,
            publish_date=publish_date,
            price=price,
            stock=stock
        )
        conn.execute(query)
        return redirect(url_for('sell_product'))

    return render_template('updateProduct.html', product={})


@app.route('/update_product/<product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    query = select([Product]).where(Product.c.product_id == product_id)
    product = conn.execute(query).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        sname = request.form['shortname']
        category = request.form['category']
        publish_date = request.form['publish_date']
        price = request.form['price']
        stock = request.form['stock']

        owner_id = user_id
        query = update(Product).where(Product.c.product_id == product_id).values(
            product_id=product_id,
            owner_id=owner_id,
            name=name,
            shortname=sname,
            category=category,
            publish_date=publish_date,
            price=price,
            stock=stock
        )
        conn.execute(query)
        return redirect(url_for('sell_product'))

    return render_template('updateProduct.html', product=product)


@app.route('/delete_product/<product_id>', methods=['GET'])
def delete_product(product_id):
    query = Product.delete().where(Product.c.product_id == product_id)
    conn.execute(query)
    return redirect(url_for('sell_product'))


def update_cart_of_user(user, new_cart):
    global cart
    cart[user] = new_cart


@app.route('/add_item/<int:product_id>', methods=['GET', 'POST'])
def add_item(product_id):
    query = select([Product]).where(Product.c.product_id == product_id)
    executed = conn.execute(query).fetchall()
    product = executed[0]
    user_cart = [get_list_from_user(user_id)][0]
    user_cart.append(product)

    update_cart_of_user(user_id, user_cart)
    total_price = calculate_cart(user_id)
    return render_template('cart.html', cart=user_cart, total_price=total_price)


@app.route('/cart_delete/<int:product_id>')
def delete_item_from_cart(product_id):
    query = select([Product]).where(Product.c.product_id == product_id)
    executed = conn.execute(query).fetchall()
    product = executed[0]

    user = getUser(user_id)
    user_cart = [get_list_from_user(user_id)][0]

    if user_cart.count(product) == 0:
        total_price = calculate_cart(user_id)
        return render_template('cart.html', cart=user_cart, total_price=total_price)

    user_cart.remove(product)
    update_cart_of_user(user_id, user_cart)
    total_price = calculate_cart(user_id)
    return render_template('cart.html', cart=user_cart, total_price=total_price)


@app.route('/show_cart')
def show_cart():
    user = getUser(user_id)
    user_cart = [get_list_from_user(user_id)][0]

    total_price = calculate_cart(user_id)
    return render_template('cart.html', cart=user_cart, total_price=total_price)


def get_budget(user_id_on):
    query = select([User]).where(User.c.userid == user_id_on)
    executed = conn.execute(query).fetchall()
    user = executed[0]
    return user[7]


def change_budget(user_id_on, budget):
    session.query(User).filter(User.c.userid == user_id_on).update({User.c.budget: budget}, synchronize_session=False)
    session.commit()


def update_product_sold(user_id_on, user_cart):
    for item in user_cart:
        prod_id = item[0]
        usr_id = user_id_on
        prod_name = item[2]
        prod_price = item[6]
        max_id_query = """SELECT max(product_sold.satis_id) AS max_1 
        FROM product_sold"""
        max_id = conn.execute(max_id_query).fetchall()[0][0]
        session.commit()
        if max_id is None:
            max_id = 0;
        max_id = max_id + 1
        print(max_id)
        a = session.query(func.max(Product_sold.c.satis_id))
        stmt = """INSERT INTO product_sold (satis_id,user_id, product_id,product_name,price,is_returned)
                VALUES ({max_id}, {user_id}, {product_id},'{product_name}',{price},0)""".format(max_id=max_id,
                                                                                                user_id=usr_id,
                                                                                                product_id=prod_id,
                                                                                                product_name=prod_name,
                                                                                                price=prod_price)
        conn.execute(stmt)
        session.commit()
        # insert = [Product_sold].insert().values(user_id=usr_id, product_id=prod_id, product_name=prod_name, product_price = prod_price )
        # Product_sold.insert().values(user_id=usr_id, product_id=prod_id, product_name=prod_name,
        #                              product_price=prod_price)
        # session.commit()


@app.route('/check_buy/<int:user_id_on>')
def check_buy(user_id_on):
    user = getUser(user_id_on)
    user_cart = [get_list_from_user(user_id)][0]

    total_price = calculate_cart(user_id)
    budget = get_budget(user_id_on)

    if budget >= total_price:
        budget = budget - total_price
        change_budget(user_id_on, budget)
        update_product_sold(user_id_on, user_cart)
        user_cart = list()
        update_cart_of_user(user_id, user_cart)
        return redirect(url_for('main'))
    else:
        return render_template('cart.html', cart=user_cart, total_price=total_price)


@app.route('/return_product')
def return_page():
    query = """SELECT product_sold.satis_id, product_sold.user_id, product_sold.product_id, product_sold.product_name, product_sold.price 
                FROM product_sold 
                WHERE product_sold.user_id = {user_id} AND product_sold.is_returned = 0 """.format(user_id=user_id)
    products_sold = conn.execute(query).fetchall()
    return render_template('return_product.html', products=products_sold, usr=user_id)


@app.route('/return_a_product/<int:satis_id>')
def return_a_product(satis_id):
    session.query(Product_sold).filter(Product_sold.c.satis_id == satis_id).update({Product_sold.c.is_returned: 1}, synchronize_session=False)
    session.commit()

    query = """SELECT product_sold.satis_id, product_sold.user_id, product_sold.product_id, product_sold.product_name, product_sold.price 
                        FROM product_sold 
                        WHERE product_sold.user_id = {user_id} AND product_sold.is_returned = 0 """.format(
        user_id=user_id)
    products_sold = conn.execute(query).fetchall()
    return render_template('return_product.html', products=products_sold, usr=user_id)

@app.route('/discounts', methods=['GET'])
def discounts():
    query = select([Product]).order_by(desc(Product.c.salePercentage)).where(Product.c.salePercentage > 0)
    sellable_products = conn.execute(query).fetchall()
    return render_template('discounts.html', products=sellable_products)


if __name__ == '__main__':
    app.run(debug=True)
