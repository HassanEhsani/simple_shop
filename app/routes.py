from flask import Blueprint, render_template, request, redirect, url_for, session
from .models import Order, OrderItem
from . import db
from .translations import t
import json
import os
from .models import User
from werkzeug.security import generate_password_hash
from flask import flash
from flask import render_template, redirect, url_for, flash, request
from app.forms import RegisterForm
from app.models import db, User
from flask_login import login_user

main = Blueprint('main', __name__)

# کمکی برای زبان
def get_lang():
    return request.args.get('lang', 'fa')

# کمکی برای بارگذاری محصولات (فرض می‌کنیم محصولات در یک فایل JSON هستند)
def load_products():
    PRODUCTS_PATH = os.path.join(os.path.dirname(__file__), 'products.json')
    with open(PRODUCTS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

@main.route('/')
def index():
    lang = get_lang()
    search_query = request.args.get('search', '')
    category = request.args.get('category', '')
    products = load_products()

    if search_query:
        products = [p for p in products if search_query.lower() in p['name'].lower()]

    if category:
        products = [p for p in products if category.lower() in p['category'].lower()]

    categories = set(p['category'] for p in products)

    return render_template('index.html', t=t, lang=lang, products=products, categories=categories)

@main.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = int(request.form['product_id'])
    products = load_products()
    product = next((p for p in products if p['id'] == product_id), None)

    if product:
        cart = session.get('cart', [])
        cart.append(product)
        session['cart'] = cart

    return redirect(url_for('main.index', lang=get_lang()))

@main.route('/cart')
def cart():
    cart = session.get('cart', [])
    total = sum(item['price'] for item in cart)
    return render_template('cart.html', cart=cart, total=total)

@main.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', [])
    total = sum(item['price'] for item in cart)

    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']

        new_order = Order(name=name, address=address, phone=phone, total=total)
        db.session.add(new_order)
        db.session.commit()

        for item in cart:
            order_item = OrderItem(product_name=item['name'], price=item['price'], order=new_order)
            db.session.add(order_item)

        db.session.commit()
        session.pop('cart', None)

        return f"Спасибо за заказ, {name}! Ваш заказ сохранён в базе данных."

    return render_template('checkout.html', cart=cart, total=total)

@main.route('/admin/orders')
def admin_orders():
    if not session.get('admin_logged_in'):
        return redirect(url_for('main.admin_login'))

    orders = Order.query.all()
    return render_template('admin_orders.html', orders=orders)

@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    lang = get_lang()

    urls_for_langs = {}
    for language_code in ['fa', 'en', 'ru']:
        args = request.args.to_dict()
        args['lang'] = language_code
        urls_for_langs[language_code] = url_for(request.endpoint, **args)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == '1234':
            session['admin_logged_in'] = True
            return redirect(url_for('main.admin_orders'))
        else:
            return t('wrong_login', lang)

    return render_template('admin_login.html', t=t, lang=lang, urls_for_langs=urls_for_langs)

@main.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('main.admin_login'))
@main.route('/register', methods=['GET', 'POST'])
def register():
    lang = get_lang()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # چک کنیم ایمیل تکراری نباشه
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('ایمیل قبلاً ثبت شده', 'danger')
            return redirect(url_for('main.register'))

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('ثبت‌نام با موفقیت انجام شد!', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html', t=t, lang=lang)

@main.route('/login', methods=['GET', 'POST'])
def login():
    lang = get_lang()

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash('ورود موفقیت‌آمیز بود!', 'success')
            return redirect(url_for('main.index', lang=lang))
        else:
            flash('ایمیل یا رمز عبور اشتباه است.', 'danger')

    return render_template('login.html', t=t, lang=lang)
