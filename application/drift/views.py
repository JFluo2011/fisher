from flask import flash, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import or_, desc

from . import drift_blueprint as drift
from ..models import Drift, Gift, db, User, Wish
from ..book.viewmodel import BookViewModel, DriftCollection
from .forms import DriftForm
from ..libs.email import send_mail
from ..libs.enums import PendingStatus


@drift.route('/drift/<int:gid>', methods=['GET', 'POST'])
@login_required
def send_drift(gid):
    current_gift = Gift.query.filter_by(id=gid).first_or_404()

    if current_gift.is_yourself_gift(current_user.id):
        flash('your can\'t request gift from yourself')
        return redirect(url_for('book.detail', isbn=current_gift.isbn))

    if not current_user.can_send_drift():
        return render_template('not_enough_beans.html', beans=current_user.beans)

    form = DriftForm(request.form)
    if (request.method == 'POST') and form.validate():
        save_drift(form, current_gift)
        send_mail(current_gift.user.email, '有人向你请求一本书', 'email/get_gift.html',
                  wisher=current_user, gift=current_gift)
        return redirect(url_for('drift.pending'))

    presenter = current_gift.user.summary
    return render_template('drift.html', presenter=presenter, user_beans=current_user.beans, form=form)


@drift.route('/pending')
@login_required
def pending():
    drifts = Drift.query.filter(
        or_(Drift.requester_id==current_user.id, Drift.presenter_id==current_user.id)
    ).order_by(desc(Drift.create_time)).all()

    return render_template('pending.html', drifts=DriftCollection(drifts, current_user.id).data)


@drift.route('/drift/<int:did>/mailed')
def mailed_drift(did):
    with db.auto_commit():
        drift_obj = Drift.query.filter_by(presenter_id=current_user.id, id=did).first_or_404()
        drift_obj.pending = PendingStatus.Success
        current_user.beans += 1
        gift = Gift.query.filter_by(id=Drift.gift_id).first_or_404()
        gift.launched = True
        wish = Wish.query.filter_by(isbn=Drift.book_isbn, uid=Drift.requester_id, launched=False).first_or_404()
        wish.launched = True

    return redirect(url_for('drift.pending'))


@drift.route('/drift/<int:did>/reject')
@login_required
def reject_drift(did):
    with db.auto_commit():
        drift_obj = Drift.query.filter_by(presenter_id=current_user.id, id=did).first_or_404()
        drift_obj.pending = PendingStatus.Reject
        requester = User.query.get_or_404(drift.requester_id)
        requester.beans += 1

    return redirect(url_for('drift.pending'))


@drift.route('/drift/<int:did>/redraw')
def redraw_drift(did):
    with db.auto_commit():
        # 超权处理 requester_id=current_user.id
        drift_obj = Drift.query.filter_by(requester_id=current_user.id, id=did).first_or_404()
        drift_obj.pending = PendingStatus.Redraw
        current_user.beans += 1

    return redirect(url_for('drift.pending'))


def save_drift(drift_form, current_gift):
    with db.auto_commit():
        drift_data = Drift()
        drift_form.populate_obj(drift_data)
        drift_data.gift_id = current_gift.id

        drift_data.requester_id = current_user.id
        drift_data.requester_nickname = current_user.nickname
        drift_data.presenter_nickname = current_gift.user.nickname
        drift_data.presenter_id = current_gift.user.id

        book = BookViewModel(current_gift.book)
        drift_data.book_title = book.title
        drift_data.book_author = book.author
        drift_data.book_img = book.image
        drift_data.book_isbn = book.isbn

        current_user.beans -= 1

        db.session.add(drift_data)
