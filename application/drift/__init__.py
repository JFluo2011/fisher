from flask import Blueprint


drift_bp = Blueprint('drift', __name__)


from . import views
