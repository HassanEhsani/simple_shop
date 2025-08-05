from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from app.translations import t

# مقداردهی اولیه
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # مقداردهی به افزونه‌ها
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # رجیستر کردن blueprint
    from app.routes import main
    app.register_blueprint(main)

    # اضافه کردن تابع ترجمه به Jinja
    app.jinja_env.globals['t'] = t

    # ✅ اضافه کردن context processors به صورت جداگانه
    @app.context_processor
    def inject_translator():
        return dict(t=t)

    @app.context_processor
    def inject_lang():
        lang = request.args.get('lang', 'fa')
        return dict(lang=lang)

    return app

# 🔻 بعد از تعریف create_app
from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
