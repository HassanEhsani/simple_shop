from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.secret_key = 'mysecret'  # برای سبد خرید

# تنظیمات دیتابیس
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# اتصال به دیتابیس
db = SQLAlchemy(app)

# -----------------------------
# مدل‌ها (جداول)
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    total = db.Column(db.Float)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100))
    price = db.Column(db.Float)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)

# -----------------------------
# بارگذاری محصولات
def load_products():
    with open('products.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# -----------------------------
# روت‌ها

# @app.route('/')
# def index():
#     products = load_products()
#     return render_template('index.html', products=products)

# @app.route('/')
# def index():
#     search_query = request.args.get('search', '')  # گرفتن مقدار جستجو از URL
#     products = load_products()

#     if search_query:
#         # فیلتر کردن محصولات بر اساس جستجو
#         products = [p for p in products if search_query.lower() in p['name'].lower()]

@app.route('/')
def index():
    search_query = request.args.get('search', '')  # جستجو
    category = request.args.get('category', '')  # دسته‌بندی
    products = load_products()

    if search_query:
        products = [p for p in products if search_query.lower() in p['name'].lower()]

    if category:
        products = [p for p in products if category.lower() in p['category'].lower()]

    categories = set(p['category'] for p in products)  # گرفتن لیست دسته‌بندی‌ها

    return render_template('index.html', products=products, categories=categories)


    return render_template('index.html', products=products)


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = int(request.form['product_id'])
    products = load_products()
    product = next((p for p in products if p['id'] == product_id), None)

    if product:
        cart = session.get('cart', [])
        cart.append(product)
        session['cart'] = cart

    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    total = sum(item['price'] for item in cart)
    return render_template('cart.html', cart=cart, total=total)


@app.route('/checkout', methods=['GET', 'POST'])
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
@app.route('/admin/orders')
def admin_orders():
    orders = Order.query.all()  # همه سفارش‌ها رو از دیتابیس می‌گیریم
    return render_template('admin_orders.html', orders=orders)


# -----------------------------
# اجرای برنامه و ساخت دیتابیس
if __name__ == '__main__':
    with app.app_context():
        print("🛠 ساخت جداول دیتابیس...")
        db.create_all()
    app.run(debug=True)
