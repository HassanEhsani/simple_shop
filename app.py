from flask import Flask, render_template, request, redirect, url_for, session
import json

app = Flask(__name__)
app.secret_key = 'mysecret'  # برای سبد خرید

# بارگذاری محصولات از فایل
def load_products():
    with open('products.json', 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/')
def index():
    products = load_products()
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
        
        # اینجا می‌تونی برای ثبت سفارش، اطلاعات رو ذخیره کنی یا ارسال کنی
        # به عنوان مثال، می‌تونیم سفارش رو در کنسول چاپ کنیم
        print(f"Новый заказ: {name}, {address}, {phone}, Итого: {total} ₽")

        # بعد از ثبت سفارش، سبد خرید پاک می‌شه
        session.pop('cart', None)

        return f"Спасибо за заказ, {name}! Мы свяжемся с вами."

    return render_template('checkout.html', cart=cart, total=total)


if __name__ == '__main__':
    app.run(debug=True)
