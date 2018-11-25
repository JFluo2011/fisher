class BookViewModel:
    def __init__(self, book):
        self.title = book['title']
        self.author = '、'.join(book['author'])
        self.binding = book['binding']
        self.publisher = book['publisher']
        self.image = book['image']
        self.price = book['price'] and str(book['price'])
        self.pubdate = book['pubdate']
        self.isbn = book['isbn']
        self.pages = book['pages']
        self.summary = book['summary'] or ''

    @property
    def intro(self):
        elements = [element for element in [self.author, self.publisher, self.price] if element]
        return ' / '.join(elements)


class BookCollection:
    def __init__(self):
        self.total = 0
        self.books = []
        self.keyword = ''

    def handle_data(self, fisher_book, keyword):
        self.total = fisher_book.total
        self.keyword = keyword
        self.books = [BookViewModel(book) for book in fisher_book.books]
