from flask import session, Flask, flash, request, redirect, render_template, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager,login_required, current_user, login_user, logout_user 
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
#from database import db


app = Flask(__name__)
app.secret_key = 'A!C@D#F$H'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.sqlite3"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user_page'

db = SQLAlchemy(app)

class Category(db.Model):
  category_id = db.Column(db.Integer, primary_key = True)
  category_name = db.Column(db.String, nullable = False)
  #product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
  products = db.relationship("Product", back_populates = "category",  cascade='all, delete-orphan')

  def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
  product_id = db.Column(db.Integer, primary_key = True)
  product_name = db.Column(db.String, nullable = False)
  unit = db.Column(db.String, nullable=False)
  rate_per_unit = db.Column(db.Float, nullable=False)
  quantity = db.Column(db.Integer, nullable=False)
  manufacture_date = db.Column(db.Date)
  expiry_date = db.Column(db.Date)
  category_id = db.Column(db.Integer, db.ForeignKey("category.category_id"))
  category = db.relationship('Category', back_populates='products')
  users = db.relationship('Association', back_populates='product')
  #category = db.relationship("Category", back_populates = "members")

  def __repr__(self):
        return f'<Product {self.product_name}>'


''' class Association(db.Model):
   id = db.Column(db.Integer, primary_key = True)
   category_id = db.Column(db.Integer, db.ForeignKey("category.category_id"))
   product_id = db.Column(db.Integer, db.ForeignKey("product.product_id"))    '''

'''with app.app_context():
   db.create_all()'''

@app.route('/')
def home():
   return render_template('home.html')

@app.route('/admin_page', methods=['GET', 'POST'])
def admin_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin@123':
            return redirect('/manager_dashboard')
        else:
            error = 'Invalid username or password'
            return render_template('admin_login.html', error=error)
    return render_template('admin_login.html')

@app.route('/manager_dashboard')
def manager_dashboard():
    categories = Category.query.all()
    return render_template('manager_dashboard.html', categories=categories)

@app.route('/AddCategory', methods=['GET', 'POST'])
def AddCategory():
    if request.method == 'POST':
        category_name = request.form['category_name']
        category = Category(category_name=category_name)
        db.session.add(category)
        db.session.commit()
        return redirect(url_for('manager_dashboard'))
    return render_template('AddCategory.html')

'''@app.route('/category/<int:category_id>')
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    return render_template('show_category.html', category=category) '''

@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    if request.method == 'POST':
        category.category_name = request.form['category_name']
        db.session.commit()
        return redirect(url_for('manager_dashboard', category_id=category.category_id))
    return render_template('edit_category.html', category=category)

@app.route('/category/<int:category_id>/delet', methods=['GET', 'POST'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if request.method == 'POST':
       db.session.delete(category)
       db.session.commit()
       return redirect(url_for('manager_dashboard'))
    return render_template('delete_category.html', category=category)







@app.route('/AddProduct/<int:category_id>', methods=['GET', 'POST'])
def AddProduct(category_id):
    if request.method == 'POST':
        product_name = request.form['product_name']
        unit = request.form['unit']
        rate_per_unit = float(request.form['rate_per_unit'])
        quantity = int(request.form['quantity'])
        manufacture_date = datetime.strptime(request.form['manufacture_date'], '%Y-%m-%d').date()
        expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d').date()
        product = Product(product_name=product_name, unit=unit, rate_per_unit=rate_per_unit,quantity=quantity, manufacture_date=manufacture_date, expiry_date=expiry_date, category_id=category_id)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('manager_dashboard'))
    category = Category.query.get_or_404(category_id)
    return render_template('AddProduct.html', category_id=category_id)

@app.route('/ActionsProduct/<int:category_id>')
def ActionsProduct(category_id):
    category = Category.query.get_or_404(category_id)
    return render_template('ActionsProduct.html', category=category)

@app.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.product_name = request.form['product_name']
        product.unit = request.form['unit']
        product.rate_per_unit = float(request.form['rate_per_unit'])
        product.quantity = int(request.form['quantity'])
        product.manufacture_date = datetime.strptime(request.form['manufacture_date'], '%Y-%m-%d').date()
        product.expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d').date()
        db.session.commit()
        return redirect(url_for('ActionsProduct', category_id=product.category_id))
    return render_template('edit_product.html', product=product)

@app.route('/product/<int:product_id>/delet', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('ActionsProduct', category_id=product.category_id))




class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    products = db.relationship('Association', back_populates='user')
    # product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    #products = db.relationship("Product", backref = "user")

    def __repr__(self):
        return f'<Category {self.name}>'
    
    def __init__(self,  username, password):
        
        self.username = username
        self.password = generate_password_hash(password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.user_id
    
class Association(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), primary_key=True)
    product_quantity = db.Column(db.Integer, nullable=False)
    user = db.relationship('User', back_populates='products')
    product = db.relationship('Product', back_populates='users')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/user_page",methods=['GET', 'POST']) 
def user_page():
  if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
             #session['user_id'] = user.user_id
             login_user(user)
             return redirect(url_for('user_dashboard'))
        elif user:
            return render_template('user_login.html', error='Incorrect Password')
        else:
            return render_template('user_login.html', error='You are not registered user. Please register!')
            
  return render_template('user_login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_match = User.query.filter_by(username=username).first()

        if user_match:                            
            return render_template('register.html', error='You are already registered. Please login')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify('User registered successfully')
    return render_template('register.html')

@app.route('/user_dashboard')
@login_required
def user_dashboard():
    categories = Category.query.all()
    user_id=current_user.user_id
    ''' if 'user_id' in session:
        user_id = session['user_id']
        #product = Product.query.filter_by(user_id=current_user.user_id).all()
        return render_template('user_dashboard.html',  user_id=user_id, categories=categories) '''
    return render_template('user_dashboard.html',  user_id=user_id, categories=categories)

@app.route('/AddtoCart/<int:product_id>', methods=['GET','POST'])
@login_required
def AddtoCart(product_id):
    product = Product.query.get_or_404(product_id)
    user_id=current_user.user_id
    if request.method == 'POST':
           product_quantity = request.form['product_quantity']
           association = Association(user_id=user_id, product_id=product_id, product_quantity=product_quantity)
           db.session.add(association)
           db.session.commit()
           return redirect(url_for('user_dashboard'))
    return render_template('AddtoCart.html', product=product)
    

@app.route('/cart')
@login_required
def cart():
    user_id=current_user.user_id
    association = Association.query.filter_by(user_id=user_id).all()
    product = Product.query.all()
    return render_template('cart.html', association=association, product=product)

@app.route('/BuyNow/<int:product_id>', methods=['GET', 'POST'])
def BuyNow(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        quantity =(int)(request.form['quantity'])
        total_p = quantity * product.rate_per_unit
        return render_template('BuyNow.html', product = product, total_p=total_p,quantity=quantity)
    
    return render_template('BuyNow.html', product = product, total_p=product.rate_per_unit,quantity=1)
    

@app.route('/OrderPlaced/<int:product_id>/<int:quantity>', methods=['GET'])
def OrderPlaced(product_id,quantity):
    product = Product.query.get(product_id)
    if(product.quantity>=quantity):
       product.quantity = product.quantity - quantity
       db.session.commit()
    elif(product.quantity<quantity):
        return 'Quantity you entered is not available in Stock. Only '+ str(product.quantity) +' are available'
    return render_template('OrderPlaced.html')

@app.route('/BuyAll', methods=['GET'])
def BuyAll():
    user_id=current_user.user_id
    association = Association.query.filter_by(user_id=user_id).all()
    product=Product.query.all()
    
    for assc in association:
        for prod in product:
             if prod.product_id == assc.product_id:
                 if prod.quantity >= assc.product_quantity:
                   prod.quantity -= assc.product_quantity
                   db.session.commit() 
                 else:
                    return 'Quantity you entered is not available in Stock. Only '+ str(prod.quantity) + 'quantity of '+ str(prod.product_name)+ ' are available'
    for assc in association:
         db.session.delete(assc)
    db.session.commit()
    return render_template('OrderPlaced.html')

@app.route('/ClearCart', methods=['GET'])
def ClearCart():
     user_id=current_user.user_id
     association = Association.query.filter_by(user_id=user_id).all()
     for assc in association:
         db.session.delete(assc)
     db.session.commit() 
     return render_template('cart.html')

@app.route('/search',methods=['GET'])
def search():
    search_query = request.args.get('search_query')
    categories = Category.query.all()
    products = Product.query.all()
    filtered_categories = []
    filtered_products = []
    filtered_catg2=[]
    f_c=0
    f_p=0
    for category in categories:
        if search_query in category.category_name:
             f_c=1
             filtered_categories.append(category)

    for category in categories:         
        for product in products:
           if search_query in product.product_name and product.category_id == category.category_id:
                 f_p=1
                 filtered_products.append(product)
                 filtered_catg2.append(category)
             
    if f_c==1:
         return render_template('user_dashboard.html',categories=filtered_categories)
    elif f_p==1:
         return render_template('user_dashboard.html', categories=filtered_catg2 , products=filtered_products) 
    return render_template('user_dashboard.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user_page'))

app.app_context().push()

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

