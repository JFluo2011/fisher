from flask import Blueprint


book_blueprint = Blueprint('book', __name__)


from . import views
