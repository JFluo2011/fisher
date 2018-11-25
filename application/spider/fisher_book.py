from flask import current_app

from application.libs.api_caller import ApiCaller


class FisherBook:
    isbn_url = 'http://t.yushu.im/v2/book/isbn/{}'
    keyword_url = 'http://t.yushu.im/v2/book/search?q={}&start={}&count={}'

    def __init__(self):
        self.total = 0
        self.books = []

    def search_by_isbn(self, keyword):
        # TODO save to database and get from database
        url = self.isbn_url.format(keyword)
        self._fill_single(ApiCaller.get(url))

    def search_by_keyword(self, keyword, page):
        url = self.keyword_url.format(keyword, self.get_start(page), current_app.config['PER_PAGE'])
        self._fill_collection(ApiCaller.get(url))

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
