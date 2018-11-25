from flask import Flask

from application.models import db, login_manager


def create_app():
    app = Flask(__name__)
    app.config.from_object('application.security')
    app.config.from_object('application.settings')

    register_blueprint(app)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'please login or register'

    with app.app_context():
        db.create_all(app=app)

    return app


def register_blueprint(app):
    from .book import book_blueprint
    from .auth import auth_blueprint
    from .trade import trade_blueprint
    app.register_blueprint(book_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(trade_blueprint)

