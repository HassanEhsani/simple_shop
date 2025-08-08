# app/__init__.py
from flask import Flask, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from app.translations import t

# مقداردهی اولیه‌ی افزونه‌ها
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # register blueprint
    from app.routes import main
    app.register_blueprint(main)

    # make translator available in templates
    app.jinja_env.globals['t'] = t

    # context processor: آدرس‌های سوئیچ زبان و زبان جاری
    @app.context_processor
    def inject_lang_helpers():
        def make_lang_urls():
            urls = {}
            endpoint = request.endpoint  # مثلا 'main.index'
            view_args = dict(request.view_args or {})

            for code in ['fa', 'en', 'ru', 'tj']:
                try:
                    args = {**view_args, 'lang': code}
                    if endpoint:
                        urls[code] = url_for(endpoint, **args)
                    else:
                        urls[code] = url_for('main.index', lang=code)
                except Exception:
                    urls[code] = url_for('main.index', lang=code)
            return urls

        current_lang = request.args.get('lang') or session.get('lang', 'fa')
        return {
            'urls_for_langs': make_lang_urls(),
            'current_lang': current_lang
        }

    # translator context (اضافی، برای اطمینان)
    @app.context_processor
    def inject_translator():
        return dict(t=t)

    return app

# user_loader بعد از تعریف create_app
from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
