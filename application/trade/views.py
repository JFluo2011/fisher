from datetime import datetime

from flask import redirect, render_template, url_for, flash, current_app
from flask_login import current_user, login_required

from . import trade_bp as trade
from ..models import db, Gift, Wish
from ..spider.fisher_book import FisherBook
from .viewmodel import MyTrades


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


@trade.route('/pending')
def pending():
    pass


@trade.route('/gifts/book/<isbn>')
@login_required
def save_to_gifts(isbn):
    book = FisherBook()
    book.search(isbn)
    if not book.first:
        pass
    else:
        Gift.save_goods(Wish, isbn, book.first.id, current_user.id)

    return redirect(url_for('book.book_detail', isbn=isbn))


@trade.route('/wish/book/<isbn>')
@login_required
def save_to_wishes(isbn):
    book = FisherBook()
    book.search(isbn)
    if not book.first:
        pass
    else:
        Wish.save_goods(Gift, isbn, book.first.id, current_user.id)

    return redirect(url_for('book.book_detail', isbn=isbn))


@trade.route('/satisfy_wish')
def satisfy_wish():
    pass


@trade.route('/gifts/redraw/<isbn>')
@login_required
def redraw_from_gifts(isbn):
    book = FisherBook()
    book.search(isbn)
    if not book.first:
        pass
    else:
        gift = Gift.query.filter_by(isbn=isbn).first_or_404()
        with db.auto_commit():
            current_user.beans -= current_app.config['BEANS_UPLOAD_ONE_BOOK']
            gift.delete()

    return redirect(url_for('trade.my_gifts'))


@trade.route('/wishes/redraw/<isbn>')
@login_required
def redraw_from_wishes(isbn):
    book = FisherBook()
    book.search(isbn)
    if not book.first:
        pass
    else:
        wish = Wish.query.filter_by(isbn=isbn).first_or_404()
        with db.auto_commit():
            wish.delete()

    return redirect(url_for('trade.my_wishes'))
