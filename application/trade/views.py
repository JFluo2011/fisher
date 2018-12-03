from datetime import datetime
from functools import wraps

from flask import redirect, render_template, url_for, flash, current_app, abort
from flask_login import current_user, login_required

from ..utils.enums import PendingStatus
from . import trade_bp as trade
from ..models import db, Gift, Wish, Drift
from ..spider.fisher_book import FisherBook
from .viewmodels import MyTrades


def book_check(func):
    @wraps(func)
    def decorator(isbn, *args, **kwargs):
        book = FisherBook()
        book.search(isbn)
        if not book.first:
            abort(404)
        else:
            return func(isbn, *args, **kwargs, bid=book.first.id)

    return decorator


@trade.route('/my_gifts')
@login_required
def my_gifts():
    gifts = Gift.get_user_goods(current_user.id)
    isbn_lst = [gift.isbn for gift in gifts]
    goods_count = Gift.get_goods_counts(Wish, isbn_lst)
    my_trades = MyTrades(gifts, goods_count)
    return render_template('trade/my_gifts.html', gifts=my_trades.trades)


@trade.route('/my_wishes')
@login_required
def my_wishes():
    wishes = Wish.get_user_goods(current_user.id)
    isbn_lst = [wish.isbn for wish in wishes]
    goods_count = Wish.get_goods_counts(Gift, isbn_lst)
    my_trades = MyTrades(wishes, goods_count)
    return render_template('trade/my_wishes.html', wishes=my_trades.trades)


@trade.route('/gifts/book/<isbn>')
@login_required
@book_check
def save_to_gifts(isbn, bid=-1):
    if Wish.query.filter_by(uid=current_user.id, bid=bid, launched=False).first():
        flash('此书籍已经在你的心愿清单中')
    else:
        gift = Gift.query.filter_by(use_base=True, bid=bid, uid=current_user.id, launched=False).first()

        if gift and gift.status:
            redraw_gift(bid)
        elif gift and (not gift.status):
            gift.restore()
        else:
            Gift.add(isbn, bid, current_user.id)

    return redirect(url_for('book.book_detail', isbn=isbn))


@trade.route('/wish/book/<isbn>')
@login_required
@book_check
def save_to_wishes(isbn, bid=-1):
    if Gift.query.filter_by(uid=current_user.id, bid=bid, launched=False).first():
        flash('此书籍已经在你的赠送清单中')
    else:
        wish = Wish.query.filter_by(use_base=True, bid=bid, uid=current_user.id, launched=False).first()

        if wish and wish.status:
            wish.delete()
        elif wish and (not wish.status):
            wish.restore()
        else:
            Wish.add(isbn, bid, current_user.id)

    return redirect(url_for('book.book_detail', isbn=isbn))


@trade.route('/gifts/redraw/<isbn>')
@login_required
@book_check
def redraw_from_gifts(isbn, bid=-1):
    redraw_gift(bid)

    return redirect(url_for('trade.my_gifts'))


@trade.route('/wishes/redraw/<isbn>')
@login_required
@book_check
def redraw_from_wishes(isbn, bid=-1):
    wish = Wish.query.filter_by(bid=bid).first_or_404()
    wish.delete()

    return redirect(url_for('trade.my_wishes'))


def redraw_gift(bid):
    gift = Gift.query.filter_by(bid=bid).first_or_404()
    drift = Drift.query.filter_by(gift_id=gift.id, pending=PendingStatus.Waiting).first()
    if drift is not None:
        flash('这个礼物正处于交易状态，请先前往鱼漂完成交易')
        return
    gift.delete()
