from flask import Flask, render_template
from flask_mail import Mail
from flask_migrate import Migrate

from .models import db, login_manager


mail = Mail()
migrate = Migrate()


def not_found(e):
    return render_template('404.html'), e.code


def create_app():
    app = Flask(__name__)
    app.config.from_object('application.security')
    app.config.from_object('application.settings')

    register_blueprint(app)

    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请登录或者注册帐号'

    with app.app_context():
        db.create_all(app=app)

    app.errorhandler(404)(not_found)
    return app


def register_blueprint(app):
    from .book import book_bp
    from .auth import auth_bp
    from .trade import trade_bp
    from .drift import drift_bp
    app.register_blueprint(book_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(trade_bp)
    app.register_blueprint(drift_bp)
