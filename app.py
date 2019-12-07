from flask import Flask, render_template, redirect, request, flash, session			# same as before
from flask_sqlalchemy import SQLAlchemy			# instead of mysqlconnection
from sqlalchemy.sql import func, expression     # ADDED THIS LINE FOR DEFAULT TIMESTAMP
from flask_migrate import Migrate			# this is new
from flask_bcrypt import Bcrypt
import re

app = Flask(__name__)
app.secret_key = "soloproject"
bcrypt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
# configurations to tell our app about the database we'll be connecting to
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shopping.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# an instance of the ORM
db = SQLAlchemy(app)
# a tool for allowing migrations/creation of tables
migrate = Migrate(app, db)
#### ADDING THIS CLASS ####
# the db.Model in parentheses tells SQLAlchemy that this class represents a table in our database

class User(db.Model):	
    __tablename__ = "user"    # optional		
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    pw = db.Column(db.String(255))
    confirm_pw = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=func.now())    # notice the extra import statement above
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class Order(db.Model):	#one to many relationship with Product; one to many with user
    __tablename__ = "order"    # optional		
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', foreign_keys=[user_id], backref="orders", cascade="all")
    product_ids = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())    # notice the extra import statement above
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class Product(db.Model):	
    __tablename__ = "product"    # optional		
    id = db.Column(db.Integer, primary_key=True)
    product_image = db.Column(db.String(255))
    product_name = db.Column(db.String(255))
    product_price = db.Column(db.Float)
    # order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    # author = db.relationship('User', foreign_keys=[author_id], backref="posts", cascade="all")
    # order = db.relationship('Order', foreign_keys=[order_id], backref="products")
    # created_at = db.Column(db.DateTime, server_default=func.now())    # notice the extra import statement above
    # updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

@app.route('/')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/on_login', methods=['POST'])
def on_login():
    is_valid = True

    if len(request.form['em']) < 1:
        is_valid = False
        flash("Email cannot be blank.")
    
    if not EMAIL_REGEX.match(request.form['em']):
        is_valid = False
        flash("Please use a valid email.")

    if is_valid:
        user_with_correct_email = User.query.filter_by(email=request.form['em']).all()

        if user_with_correct_email:
            if bcrypt.check_password_hash(user_with_correct_email[0].pw, request.form['pw']):
                session['id'] = user_with_correct_email[0].id
                return redirect('/homepage')

            else:
                flash("Password is not valid.")
                return redirect('/login')
        else:
            flash("Email is not valid.")
            return redirect('/login')
    else:
        return redirect('/login')

@app.route('/register', methods=['POST'])
def on_register():
     is_valid = True
     
     if len(request.form['fn']) < 1:
        is_valid = False
        flash("First name cannot be blank")

     if len(request.form['ln']) < 1:
        is_valid = False
        flash("Last name cannot be blank")
    
     if len(request.form['pw']) < 1:
        is_valid = False
        flash("Password cannot be blank")

     if request.form['pw'] != request.form['c_pw']:
        is_valid = False
        flash("Password don't match.")

     if not EMAIL_REGEX.match(request.form['em']):
        is_valid = False
        flash("Please use a valid email.")

     if not is_valid:
        return redirect('/')
     else:
        hashed_pw = bcrypt.generate_password_hash(request.form['pw'])

        new_user = User(first_name=request.form['fn'], last_name=request.form['ln'], email=request.form['em'], pw=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        print(new_user)
        return redirect('/homepage')

@app.route('/homepage')
def homepage():
    if 'id' not in session:
        return redirect('/')
    print("******")
    user_with_correct_id = User.query.filter_by(id=session['id']).all()
    if user_with_correct_id:
        user_data =  {}
        user_data['first_name'] = user_with_correct_id[0].first_name
    products = Product.query.all()
    return render_template('product.html', user=user_data, products=products)

@app.route('/addShoppingCart', methods=['POST'])
def addShoppingCart():
    return redirect('/shoppingcart')

@app.route('/shoppingcart')
def shoppingcart():
    if 'id' not in session:
        return redirect('/')
    print("******")
    user_with_correct_id = User.query.filter_by(id=session['id']).all()
    if user_with_correct_id:
        user_data =  {}
        user_data['first_name'] = user_with_correct_id[0].first_name
    # products = Product.query.filter_by()
    return render_template('shoppingcart.html', user=user_data)

@app.route('/complete')
def complete():
    if 'id' not in session:
        return redirect('/')
    print("******")
    user_with_correct_id = User.query.filter_by(id=session['id']).all()
    if user_with_correct_id:
        user_data =  {}
        user_data['first_name'] = user_with_correct_id[0].first_name
    return render_template('complete.html', user=user_data)

@app.route('/logout')
def on_logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)