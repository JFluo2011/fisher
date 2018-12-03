class TradeInfo:
    def __init__(self, trade):
        self.id = trade.id
        self.nickname = trade.user.nickname
        date = trade.create_datetime
        self.date = date.strftime('%Y-%m-%d') if date else 'unknown'


class Trades:
    def __init__(self, trades):
        self.total = 0
        self.trade_lst = []
        self._handle_data(trades)

    def _handle_data(self, trades):
        self.total = len(trades)
        self.trade_lst = [TradeInfo(trade) for trade in trades]


class MyTrade:
    def __init__(self, trade_id, book, count):
        self.id = trade_id
        self.book = book
        self.trades_count = count


class MyTrades:
    def __init__(self, trades_of_mine, trade_count_lst):
        self._trades_of_mine = trades_of_mine
        self._trade_count_lst = trade_count_lst
        self.trades = []
        self._handle_data()

    def _handle_data(self):
        self.trades = [self._build(trade) for trade in self._trades_of_mine]

    def _build(self, trade):
        count = 0
        for count_trade in self._trade_count_lst:
            if count_trade.isbn == trade.isbn:
                count = count_trade.count
                break
        return MyTrade(trade.id, trade.book, count)
