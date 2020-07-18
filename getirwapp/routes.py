from flask import render_template, flash, redirect, url_for, request, jsonify
from getirwapp import app, db, bcrypt
from getirwapp.forms import RegistrationForm, LoginForm, UpdateAccountForm, SearchForm
from getirwapp.models import User, Product
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/home")
@app.route("/")
def home():
    return render_template('home.html')


@app.route("/register", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, tel_no=form.tel_no.data, address=form.address.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}! You can now Login!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET','POST'] )
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful! Please check your email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account", methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.tel_no = form.tel_no.data
        current_user.address = form.address.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.tel_no.data = current_user.tel_no
        form.address.data = current_user.address
    image_file = url_for('static', filename='profile_pics/default.jpg')
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    #form.category.choices = [ (product.product_category) for product in Product.query.distinct() ]
    #print(form.category.choices)

    query = db.session.query(Product.product_category.distinct().label("product_category"))
    form.category.choices = [ (product.product_category) for product in query.all()]

    search_pressed = False
    if form.validate_on_submit():
        search_pressed = True

    return render_template('search.html', title='Search', form=form, search_pressed=search_pressed)

@app.route('/product/<get_product>')
def prod(get_product):
    product_data = Product.query.filter_by(product_category=get_product).all()
    prodArray = []
    for product in product_data:
        prodObj = {}
        prodObj['id'] = product.product_id
        prodObj['name'] = product.product_name
        prodArray.append(prodObj)
    return jsonify({'prodlist' : prodArray})

def arrange_string(s):
    s = str(s).replace("(","")
    s = str(s).replace("'", "")
    s = str(s).replace(")", "")
    s = str(s).replace(",", "")
    return s