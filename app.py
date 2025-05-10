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

if __name__ == '__main__':
    app.run(debug=True)
