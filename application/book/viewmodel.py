from ..libs.enums import PendingStatus


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


class DriftViewModel:
    def __init__(self, drift, current_user_id):
        self._drift = drift
        self._current_user_id = current_user_id
        self.data = self._make_data()

    def _requester_or_presenter(self):
        if self._drift.requester_id == self._current_user_id:
            return 'requester'
        return 'presenter'

    def _make_data(self):
        role = self._requester_or_presenter()
        pending_status = PendingStatus.pending_str(self._drift.pending, role)
        return {
            'role': role,
            'drift_id': self._drift.id,
            'book_title': self._drift.book_title,
            'book_author': self._drift.book_author,
            'book_img': self._drift.book_img,
            'date': self._drift.create_datetime.strftime('%Y-%m-%d'),
            'message': self._drift.message,
            'address': self._drift.address,
            'mobile': self._drift.mobile,
            'recipient_name': self._drift.recipient_name,
            'status': self._drift.pending,
            'status_str': pending_status,
            'target_name': self._drift.requester_nickname if role != 'requester' else self._drift.presenter_nickname,
        }


class DriftCollection:
    def __init__(self, drifts, current_user_id):
        self._drifts = drifts
        self._current_user_id = current_user_id
        self.data = []
        self._handle_data()

    def _handle_data(self):
        self.data = [DriftViewModel(drift, self._current_user_id).data for drift in self._drifts]
