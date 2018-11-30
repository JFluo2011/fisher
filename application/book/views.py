from flask import request, render_template, flash, redirect, url_for
from flask_login import current_user

from . import book_bp as book
from .forms import SearchForm
from ..spider.fisher_book import FisherBook
from .viewmodel import BookCollection
from ..models import Gift, Wish
from ..trade.viewmodel import Trades


@book.route('/index')
def index():
    gifts = Gift.recent()
    books = [gift.book for gift in gifts]
    return render_template('book/index.html', books=books)


@book.route('/book/<isbn>')
def book_detail(isbn):
    has_in_gifts = False
    has_in_wishes = False
    fisher_book = FisherBook()
    fisher_book.search(isbn)
    if not fisher_book.first:
        flash(f'未找到目标书籍:{isbn}')
        return redirect(url_for('book.index'))

    if current_user.is_authenticated:
        if Gift.get_book_goods(fisher_book.first.id, current_user.id):
            has_in_gifts = True
        if Wish.get_book_goods(fisher_book.first.id, current_user.id):
            has_in_wishes = True

    gifts = Trades(Gift.get_book_goods(fisher_book.first.id))
    wishes = Trades(Wish.get_book_goods(fisher_book.first.id))

    return render_template('book/book_detail.html', book=fisher_book.first,
                           has_in_wishes=has_in_wishes, has_in_gifts=has_in_gifts, wishes=wishes, gifts=gifts)


@book.route('/book/search/')
def search():
    form = SearchForm(request.args)
    books = BookCollection()
    if form.validate():
        page = form.page.data
        keyword = form.keyword.data
        fisher_book = FisherBook()
        from_db = fisher_book.search(keyword, page=page)
        books.handle_data(fisher_book, keyword, from_db)

    return render_template('book/search_result.html', books=books, wishes=[], gifts=[])

