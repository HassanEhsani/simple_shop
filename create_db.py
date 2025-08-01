import os
from app import create_app, db
from app.models import User


# ساخت پوشه instance اگه وجود نداشته باشه
os.makedirs(os.path.join(os.path.dirname(__file__), 'instance'), exist_ok=True)

app = create_app()

with app.app_context():
    db.create_all() 
    print("✅ Database created successfully!")
