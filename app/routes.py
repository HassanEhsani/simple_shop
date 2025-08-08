# app/routes.py
import os, json
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .models import Order, OrderItem, User
from . import db
from .translations import t
from flask_login import login_user, logout_user, login_required, current_user

main = Blueprint('main', __name__)

# helper
def get_lang():
    # اول پارامتر URL، بعد session، در نهایت fa
    lang = request.args.get('lang')
    if lang:
        session['lang'] = lang
        return lang
    return session.get('lang', 'fa')

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

    categories = sorted(set(p['category'] for p in products))
    return render_template('index.html', t=t, lang=lang, products=products, categories=categories)


@main.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    lang = get_lang()
    product_id = int(request.form['product_id'])
    products = load_products()
    product = next((p for p in products if p['id'] == product_id), None)

    if product:
        cart = session.get('cart', [])
        cart.append(product)
        session['cart'] = cart
        flash(t('product_added_to_cart', lang), 'success')

    return redirect(url_for('main.index', lang=lang))


@main.route('/cart')
def cart():
    lang = get_lang()
    cart = session.get('cart', [])
    total = sum(item['price'] for item in cart)
    return render_template('cart.html', cart=cart, total=total, lang=lang)


@main.route('/checkout', methods=['GET', 'POST'])
def checkout():
    lang = get_lang()
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
        flash(t('submit_order', lang), 'success')
        return redirect(url_for('main.index', lang=lang))

    return render_template('checkout.html', cart=cart, total=total, lang=lang)


@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    lang = get_lang()
    urls_for_langs = {}
    for code in ['fa', 'en', 'ru', 'tj']:
        args = request.args.to_dict()
        args['lang'] = code
        try:
            urls_for_langs[code] = url_for(request.endpoint, **args)
        except Exception:
            urls_for_langs[code] = url_for('main.index', lang=code)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == '1234':
            session['admin_logged_in'] = True
            return redirect(url_for('main.index', lang=lang))
        else:
            flash(t('wrong_login', lang), 'danger')

    return render_template('admin_login.html', t=t, lang=lang, urls_for_langs=urls_for_langs)


@main.route('/admin/logout')
def admin_logout():
    lang = get_lang()
    session.pop('admin_logged_in', None)
    flash(t('logout_success', lang), 'info')
    return redirect(url_for('main.admin_login', lang=lang))


@main.route('/register', methods=['GET', 'POST'])
def register():
    lang = get_lang()

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form.get('name') or ''

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash(t('email_already_registered', lang), 'danger')
            return redirect(url_for('main.register', lang=lang))

        user = User(email=email, name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash(t('register_success', lang), 'success')
        return redirect(url_for('main.login', lang=lang))

    return render_template('register.html', lang=lang)


@main.route('/login', methods=['GET', 'POST'])
def login():
    lang = get_lang()

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash(t('login_success', lang) if 'login_success' in t.__code__.co_consts else t('login', lang), 'success')
            return redirect(url_for('main.dashboard', lang=lang))
        else:
            flash(t('wrong_login', lang), 'danger')

    return render_template('login.html', t=t, lang=lang)


@main.route('/logout')
@login_required
def logout():
    lang = get_lang()
    logout_user()
    flash(t('logout_success', lang), 'info')
    return redirect(url_for('main.login', lang=lang))


# @main.route('/dashboard')
# @login_required
# def dashboard():
#     lang = get_lang()
#     return render_template('dashboard.html', lang=lang, user=current_user)


@main.route('/profile/<lang>')
@login_required
def profile(lang):
    return render_template('profile.html', lang=lang, user=current_user)


@main.route('/orders/<lang>')
@login_required
def orders(lang):
    return render_template('orders.html', lang=lang, user=current_user)


@main.route('/settings/<lang>')
@login_required
def settings(lang):
    return render_template('settings.html', lang=lang, user=current_user)


@main.route('/set_lang/<lang_code>')
def set_lang(lang_code):
    session['lang'] = lang_code
    return redirect(request.referrer or url_for('main.index', lang=lang_code))

@main.route('/dashboard')
@login_required
def dashboard():
    lang = get_lang()

    # آمار کلی
    total_orders = Order.query.count()
    total_users = User.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total)).scalar() or 0

    # لیست سفارش‌ها
    orders = Order.query.order_by(Order.id.desc()).limit(5).all()

    return render_template(
        'dashboard.html',
        lang=lang,
        t=t,
        total_orders=total_orders,
        total_users=total_users,
        total_revenue=total_revenue,
        orders=orders
    )


@main.route('/admin/orders/<lang>')
@login_required
def admin_orders(lang):
    # می‌تونی شرط بزاری که فقط مدیر اجازه داشته باشه، مثلا:
    if not session.get('admin_logged_in'):
        flash(t('access_denied', lang), 'danger')
        return redirect(url_for('main.admin_login', lang=lang))
    
    orders = Order.query.order_by(Order.id.desc()).all()
    return render_template('admin_orders.html', lang=lang, orders=orders)
