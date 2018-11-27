from collections import namedtuple

from ..book.viewmodel import BookViewModel


MyTrade = namedtuple('MyGift', 'id, book, trades_count')


class TradeInfo:
    def __init__(self, trades):
        self.total = 0
        self.trade_lst = []
        self._handle_data(trades)

    def _handle_data(self, trades):
        self.total = len(trades)
        self.trade_lst = [self._make_trade(trade) for trade in trades]

    @staticmethod
    def _make_trade(trade):
        date = trade.create_datetime
        if date:
            date = date.strftime('%Y-%m-%d')
        else:
            date = 'unknown'
        return {
            'user_name': trade.user.nickname,
            'date': date,
            'id': trade.id,
        }


class MyTrades:
    def __init__(self, trades_of_mine, trade_count_lst):
        self._trades_of_mine = trades_of_mine
        self._trade_count_lst = trade_count_lst
        self.trades = self._handle_data()

    def _handle_data(self):
        return [self._build(trade) for trade in self._trades_of_mine]

    def _build(self, trade):
        count = 0
        for trade_count in self._trade_count_lst:
            if trade.isbn == trade_count.isbn:
                count = trade_count.count
                break

        return MyTrade(trade.id, BookViewModel(trade.book), count)
