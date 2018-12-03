from ..utils.enums import PendingStatus


class DriftData:
    def __init__(self, drift, current_user_id):
        self._drift = drift
        self._current_user_id = current_user_id
        self.data = {}
        self._fill_data()

    def _fill_data(self):
        role = self._requester_or_presenter()

        self.data = {
            'role': role,
            'drift_id': self._drift.id,
            'recipient_name': self._drift.recipient_name,
            'address': self._drift.address,
            'mobile': self._drift.mobile,
            'message': self._drift.message,
            'date': self._drift.create_datetime.strftime('%Y-%m-%d'),
            'book_title': self._drift.book_title,
            'book_author': self._drift.book_author,
            'book_img': self._drift.book_img,
            'status': self._drift.pending,
            'presenter_nickname': self._drift.presenter_nickname,
            'status_str': PendingStatus.pending_str(self._drift.pending, role),
            'target_name': self._drift.requester_nickname if role != 'requester' else self._drift.presenter_nickname,
        }

    def _requester_or_presenter(self):
        if self._drift.requester_id == self._current_user_id:
            return 'requester'
        return 'presenter'


class DriftCollection:
    def __init__(self, drifts, current_user_id):
        self._drifts = drifts
        self._current_user_id = current_user_id
        self.data = []
        self._handle_data()

    def _handle_data(self):
        self.data = [DriftData(drift, self._current_user_id).data for drift in self._drifts]
