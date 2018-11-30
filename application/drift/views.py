from flask import render_template, redirect, request, url_for
from flask_login import login_required, current_user

from . import drift_bp as drift
from .forms import DriftForm
from ..models import Gift


@drift.route('/drift/<gid>', methods=['GET', 'POST'])
@login_required
def send_drift(gid):
    form = DriftForm(request.form)
    presenter = Gift.query.get(gid)

    if (request.method == 'POST') and form.validate():
        pass

    return render_template('drift.html', presenter=presenter.user.summary, user_beans=current_user.beans, form=form)
