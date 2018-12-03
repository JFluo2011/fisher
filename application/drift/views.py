from flask import render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_, desc

from application.utils.email import send_mail
from . import drift_bp as drift
from .forms import DriftForm
from ..models import db, Gift, Drift, User, Wish
from ..utils.enums import PendingStatus
from .viewmodels import DriftCollection


@drift.route('/drift/<gid>', methods=['GET', 'POST'])
@login_required
def send_drift(gid):
    form = DriftForm(request.form)
    gift = Gift.query.get_or_404(gid)

    if gift.is_yourself_gift(current_user.id):
        flash('你不能想自己请求礼物')
        return redirect(url_for('book.book_detail', isbn=gift.isbn))

    if not current_user.can_send_drift():
        return render_template('drift/not_enough_beans.html', beans=current_user.beans)

    if (request.method == 'POST') and form.validate():
        save_drift(form, gift)
        send_mail(gift.user.email, '有人向你请求一本书', 'email/get_gift.html',
                  wisher=current_user, gift=gift)
        return redirect(url_for('drift.pending'))

    return render_template('drift/drift.html', presenter=gift.user.summary, user_beans=current_user.beans, form=form)


@drift.route('/drift/<int:did>/mailed')
@login_required
def mailed_drift(did):
    drift_obj = Drift.query.filter_by(presenter_id=current_user.id, id=did).first_or_404()
    gift = Gift.query.get_or_404(drift_obj.gift_id)
    wish = Wish.query.filter_by(isbn=Drift.book_isbn, uid=Drift.requester_id, launched=False).first_or_404()
    with db.auto_commit():
        drift_obj.pending = PendingStatus.Success
        current_user.beans += 1
        gift.launched = True
        wish.launched = True

    return redirect(url_for('drift.pending'))


@drift.route('/drift/<int:did>//reject_drift')
@login_required
def reject_drift(did):
    drift_obj = Drift.query.filter_by(presenter_id=current_user.id, id=did).first_or_404()
    with db.auto_commit():
        drift_obj.pending = PendingStatus.Reject
        User.query.get_or_404(drift_obj.requester_id).beans += 1

    return redirect(url_for('drift.pending'))


@drift.route('/drift/<int:did>/redraw')
@login_required
def redraw_drift(did):
    drift_obj = Drift.query.filter_by(requester_id=current_user.id, id=did).first_or_404()
    with db.auto_commit():
        drift_obj.pending = PendingStatus.Redraw
        current_user.beans += 1

    return redirect(url_for('drift.pending'))


@drift.route('/pending')
@login_required
def pending():
    drifts = Drift.query.filter(
        or_(Drift.requester_id==current_user.id, Drift.presenter_id==current_user.id)
    ).order_by(desc(Drift.create_time)).all()

    return render_template('drift/pending.html', drifts=DriftCollection(drifts, current_user.id).data)


@drift.route('/drift/<int:wid>/satisfy')
@login_required
def satisfy_wish(wid):
    wish = Wish.query.get_or_404(wid)
    gift = Gift.query.filter_by(uid=current_user.id, isbn=wish.isbn).first()
    if not gift:
        flash('你还没上传此书，请点击"加入到赠送清单"添加此书。添加前，请确保自己可以赠送此书')
    else:
        send_mail(wish.user.email, '有人想赠送你一本书', 'email/satisfy_wish.html', wish=wish, gift=gift)
        flash('已向他/她发送了一封邮件，如果他/她愿意接受你的赠送，你将收到一个鱼漂')

    return redirect(url_for('book.book_detail', isbn=wish.isbn))


def save_drift(form, gift):
    drift_obj = Drift()
    drift_obj.recipient_name = form.recipient_name.data
    drift_obj.address = form.address.data
    drift_obj.mobile = form.mobile.data
    drift_obj.message = form.message.data
    drift_obj.book_isbn = gift.isbn
    drift_obj.book_title = gift.book.title
    drift_obj.book_author = gift.book.author
    drift_obj.book_img = gift.book.image
    drift_obj.requester_id = current_user.id
    drift_obj.requester_nickname = current_user.nickname
    drift_obj.presenter_id = gift.user.id
    drift_obj.gift_id = gift.id
    drift_obj.presenter_nickname = gift.user.nickname
    drift_obj.pending = PendingStatus.Waiting
    with db.auto_commit():
        current_user.beans -= 1
        db.session.add(drift_obj)
