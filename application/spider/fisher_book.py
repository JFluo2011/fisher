from flask import current_app
from sqlalchemy import or_

from ..utils.api_caller import ApiCaller
from ..utils.helper import keyword_is_isbn
from ..models import Book


class FisherBook:
    keyword_url = 'http://t.yushu.im/v2/book/search?q={}&start={}&count={}'
    isbn_url = 'http://t.yushu.im/v2/book/isbn/{}'

    def __init__(self):
        self.total = 0
        self.from_db = False
        self.books = []

    def search(self, keyword, page=0):
        if keyword_is_isbn(keyword):
            self._search_by_isbn(keyword)
        else:
            self._search_by_keyword(keyword, page)
        if self.from_db:
            print('search_from_db')
        return self.from_db

    def _search_by_isbn(self, keyword):
        url = self.isbn_url.format(keyword)
        self._search_from_db(keyword)
        if not self.books:
            self.from_db = False
            data = ApiCaller.get(url)
            self._fill_single(data)

    def _search_by_keyword(self, keyword, page):
        url = self.keyword_url.format(keyword, self.get_start(page), current_app.config['PER_PAGE'])
        data = ApiCaller.get(url)
        if not data:
            self._search_from_db(keyword, page)
        else:
            self._fill_collection(data)

    def _search_from_db(self, keyword, page=None):
        self.from_db = True
        if page is None:
            self.total = 1
            self.books.append(Book.query.filter_by(isbn=keyword).first())
        else:
            books = Book.query.filter(or_(Book.title.like(keyword), Book.author.like(keyword))).all()
            self.total = len(books)
            start = (page-1)*current_app.config['PER_PAGE']
            end = page*current_app.config['PER_PAGE']
            self.books.extend(books[start:end])

    @staticmethod
    def get_start(page):
        return (page - 1) * current_app.config['PER_PAGE']

    def _fill_single(self, data):
        if data:
            self.total = 1
            self.books.append(data)

    def _fill_collection(self, data):
        if data:
            self.total = data['total']
            self.books = data['books']

    @property
    def first(self):
        return self.books[0] if self.total >= 1 else None
