from app import create_app, db

app = create_app()

# این قسمت فقط برای اجرا در لوکال
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
