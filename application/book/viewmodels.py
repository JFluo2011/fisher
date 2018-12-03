from ..models import Book, db


class BookCollection:
    def __init__(self):
        self.total = 0
        self.keyword = ''
        self.books = []

    def handle_data(self, fisher_book, keyword, from_db):
        self.total = fisher_book.total
        self.keyword = keyword
        if from_db:
            self.books = fisher_book.books
        else:
            self.books = [Book(book) for book in fisher_book.books]
            self.save_to_db()

    def save_to_db(self):
        books = [book for book in self.books if (Book.query.filter_by(isbn=book.isbn).first() is None)]
        with db.auto_commit():
            db.session.add_all(books)
