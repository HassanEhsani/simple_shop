from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from app.translations import t

# مقداردهی اولیه
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()  # 🔹 LoginManager را اینجا ساختیم
login_manager.login_view = 'main.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    

    # مقداردهی به افزونه‌ها
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)         # 🔹 اضافه شد
    login_manager.login_view = 'main.login'  # 🔹 مسیر ویو لاگین

    from app.routes import main
    app.register_blueprint(main)
    app.jinja_env.globals['t'] = t

    return app

# 🔹 تابعی که Flask-Login برای لود کردن یوزر از دیتابیس نیاز داره
from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
