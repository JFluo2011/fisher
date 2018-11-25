from flask import request, render_template, flash, current_app, redirect, url_for
from flask_login import login_required, current_user

from .forms import SearchForm
from ..spider.fisher_book import FisherBook
from ..libs.helper import keyword_is_isbn
from . import book_blueprint as book
from ..models import Gift, Wish
from ..trade.viewmodel import TradeInfo
from .viewmodel import BookCollection, BookViewModel


@book.route('/book/search')
def search():
    form = SearchForm(request.args)
    books = BookCollection()
    # if form.validate_on_submit():
    if form.validate():
        keyword = form.keyword.data
        page = form.page.data
        fisher_book = FisherBook()
        if keyword_is_isbn(keyword):
            fisher_book.search_by_isbn(keyword)
        else:
            fisher_book.search_by_keyword(keyword, page=page)
            books.handle_data(fisher_book, keyword)
    else:
        flash('搜索的关键字不符合要求，请重新输入关键字')
    return render_template('book/search_result.html', books=books, wishes=[], gifts=[])


@book.route('/book/<isbn>/book_detail')
def book_detail(isbn):
    has_in_gifts = False
    has_in_wishes = False

    if current_user.is_authenticated:
        if Gift.get_book_gifts(isbn=isbn, uid=current_user.id):
            has_in_gifts = True
        if Wish.get_book_wishes(isbn=isbn, uid=current_user.id):
            has_in_wishes = True

    gifts = TradeInfo(Gift.get_book_gifts(isbn=isbn))
    wishes = TradeInfo(Wish.get_book_wishes(isbn=isbn))

    fisher_book = FisherBook()
    fisher_book.search_by_isbn(isbn)
    book_info = BookViewModel(fisher_book.first)

    return render_template('book/book_detail.html', book=book_info, gifts=gifts,
                           wishes=wishes, has_in_gifts=has_in_gifts, has_in_wishes=has_in_wishes)


@book.route('/book/redraw_from_gifts')
def redraw_from_gifts():
    pass


@book.route('/book/redraw_from_wish')
def redraw_from_wish():
    pass


@book.route('/index')
def index():
    recent_gift = Gift.recent()
    books = [BookViewModel(gift.book) for gift in recent_gift]
    return render_template('index.html', books=books)


@book.route('/book/pending')
def pending():
    pass


@book.route('/book/mailed_drift')
def mailed_drift():
    pass


@book.route('/book/reject_drift')
def reject_drift():
    pass


@book.route('/book/redraw_drift')
def redraw_drift():
    pass


@book.route('/book/send_drift')
def send_drift():
    pass
