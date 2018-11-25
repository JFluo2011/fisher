from flask import render_template, redirect, url_for, current_app, flash
from flask_login import login_required, current_user

from . import trade_blueprint as trade
from ..models import db, Gift, Wish
from .viewmodel import MyTrades


@trade.route('/gifts')
@login_required
def gifts():
    return 'gifts'


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


@trade.route('/wish/satisfy_wish')
@login_required
def satisfy_wish():
    pass


