from flask import render_template, redirect, url_for, current_app, flash
from flask_login import login_required, current_user

from . import trade_blueprint as trade
from ..models import db, Gift, Wish, Drift
from .viewmodel import MyTrades
from ..libs.enums import PendingStatus
from ..libs.email import send_mail


@trade.route('/gifts/book/<isbn>')
@login_required
def save_to_gifts(isbn):
    if not current_user.can_save_to_list(isbn):
        flash('this book already in your gift list or wish list')
    else:
        with db.auto_commit():
            gift = Gift()
            gift.isbn = isbn
            gift.uid = current_user.id
            current_user.beans += current_app.config['BEANS_UPLOAD_ONE_BOOK']
            db.session.add(gift)

    return redirect(url_for('book.book_detail', isbn=isbn))


@trade.route('/my_wishes')
def my_wishes():
    uid = current_user.id
    wishes_of_mine = Wish.get_user_wishes(uid)
    isbn_lst = [wish.isbn for wish in wishes_of_mine]
    gift_count_lst = Wish.get_gift_counts(isbn_lst)
    my_wish_obj = MyTrades(wishes_of_mine, gift_count_lst)
    return render_template('my_wish.html', wishes=my_wish_obj.trades)


@trade.route('/my_gifts')
def my_gifts():
    uid = current_user.id
    gifts_of_mine = Gift.get_user_gifts(uid)
    isbn_lst = [gift.isbn for gift in gifts_of_mine]
    wish_count_lst = Gift.get_wish_counts(isbn_lst)
    my_gifts_obj = MyTrades(gifts_of_mine, wish_count_lst)
    return render_template('my_gifts.html', gifts=my_gifts_obj.trades)


@trade.route('/wish/book/<isbn>')
@login_required
def save_to_wishes(isbn):
    if not current_user.can_save_to_list(isbn):
        flash('this book already in your gift list or wish list')
    else:
        with db.auto_commit():
            wish = Wish()
            wish.isbn = isbn
            wish.uid = current_user.id
            db.session.add(wish)

    return redirect(url_for('book.book_detail', isbn=isbn))


@trade.route('/satisfy/wish/<int:wid>')
@login_required
def satisfy_wish(wid):
    wish = Wish.query.get_or_404(wid)
    gift = Gift.query.filter_by(uid=current_user.id, isbn=wish.isbn).first_or_404()
    if not gift:
        flash('你还没上传此书，请点击"加入到赠送清单"添加此书。添加前，请确保自己可以赠送此书')
    else:
        send_mail(wish.user.email, '有人想赠送你一本书', 'email/satisfy_wish.html', wish=wish, gift=gift)
        flash('已向他/她发送了一封邮件，如果他/她愿意接受你的赠送，你将收到一个鱼漂')

    return redirect(url_for('book.book_detail', isbn=wish.isbn))


@trade.route('/gifts/<gid>/redraw')
def redraw_from_gifts(gid):
    gift = Gift.query.filter_by(id=gid, launched=False).first_or_404()
    drift = Drift.query.filter_by(gift_id=gid, pending=PendingStatus.Waiting).first_or_404()
    if drift is not None:
        flash('这个礼物正处于交易状态，请先前往鱼漂完成交易')
    else:
        with db.auto_commit():
            current_user.beans -= current_user.config['BEANS_UPLOAD_ONE_BOOK']
            gift.delete()

    return redirect(url_for('trade.my_gifts'))


@trade.route('/wish/book/<isbn>/redraw')
def redraw_from_wish(isbn):
    wish = Wish.query.filter_by(isbn=isbn, launched=False).first_or_404()
    with db.auto_commit():
        wish.delete()

    return redirect(url_for('trade.my_wishes'))
