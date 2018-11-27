from enum import Enum


class PendingStatus(Enum):
    Waiting = 1
    Success = 2
    Reject = 3
    Redraw = 4

    @classmethod
    def pending_str(cls, status, key):
        key_map = {
            cls.Waiting: {
                'requester': '等待对方邮寄',
                'presenter': '等待你邮寄',
            },
            cls.Success: {
                'requester': '对方已邮寄',
                'presenter': '你已邮寄，交易完成',
            },
            cls.Reject: {
                'requester': '对方已拒绝',
                'presenter': '你已拒绝',
            },
            cls.Redraw: {
                'requester': '你已撤销',
                'presenter': '对方已撤销',
            },
        }
        return key_map[status][key]
