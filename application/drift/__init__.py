from flask import Blueprint


drift_blueprint = Blueprint('drift', __name__)


from . import views
