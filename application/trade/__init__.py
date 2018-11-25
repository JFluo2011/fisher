from flask import Blueprint


trade_blueprint = Blueprint('trade', __name__)

from . import views
