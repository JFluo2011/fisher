from contextlib import contextmanager
from datetime import datetime
from collections import namedtuple

from flask import current_app, flash
from sqlalchemy.ext.declarative import declared_attr
from flask_sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy import Column, Integer, String, SmallInteger, TEXT, Boolean, Float, ForeignKey, desc, func
from sqlalchemy.orm import relationship
from flask_login import UserMixin, LoginManager, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer

from .utils.enums import PendingStatus


EachGoodsCount = namedtuple('EachGiftWishCount', 'count, isbn')
login_manager = LoginManager()


class SubSQLAlchemy(SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as err:
            self.session.rollback()
            raise err


class SubQuery(BaseQuery):
    def filter_by(self, use_base=False, **kwargs):
        if not use_base and ('status' not in kwargs.keys()):
            kwargs.update({'status': True})
        return super().filter_by(**kwargs)


db = SubSQLAlchemy(query_class=SubQuery)


class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    create_time = Column('create_time', Integer)
    status = Column(Boolean, default=True)

    def __init__(self):
        self.create_time = int(datetime.now().timestamp())

    def change_status(self):
        self.status = not self.status
        if self.status:
            self.create_time = int(datetime.now().timestamp())
            flash('添加到清单成功')
        else:
            flash('取消成功')

    @property
    def create_datetime(self):
        if self.create_time:
            return datetime.fromtimestamp(self.create_time)

    def delete(self):
        self.status = False


class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String(50), unique=True, nullable=False)
    # summary = Column(String(1000))
    summary = Column(TEXT)
    author = Column(String(100), default='佚名')
    publisher = Column(String(50))
    price = Column(String(50))
    pages = Column(String(50))
    pubdate = Column(String(50))
    isbn = Column(String(15), nullable=False, unique=True)
    binding = Column(String(20))
    image = Column(String(50))

    def __init__(self, book):
        super().__init__()
        self.id = book['id']
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


class User(UserMixin, Base):
    __tablename__ = 'users'
    nickname = Column(String(24), nullable=False)
    phone_number = Column(String(18), unique=True)
    email = Column(String(50), unique=True, nullable=True)
    confirmed = Column(Boolean, default=False)
    beans = Column(Float, default=0)
    send_counter = Column(Integer, default=0)
    receive_counter = Column(Integer, default=0)
    wx_open_id = Column(String(50))
    wx_name = Column(String(32))
    _hash_password = Column('password', String(128), nullable=False)

    # @property
    # def send_receive(self):
    #     return '/'.join([str(self.send_counter), str(self.receive_counter)])

    @property
    def password(self):
        return self._hash_password
        # raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self._hash_password = generate_password_hash(password)

    @property
    def summary(self):
        return {
            'nickname': self.nickname,
            'beans': self.beans,
            'email': self.email,
            'send_receive': str(self.send_counter) + '/' + str(self.receive_counter),
        }

    def can_save_to_list(self, bid):
        gift = Gift.query.filter_by(uid=self.id, bid=bid, launched=False).first()
        wish = Wish.query.filter_by(uid=self.id, bid=bid, launched=False).first()
        if not gift and not wish:
            return True
        else:
            return False

    def check_password(self, password):
        return check_password_hash(self._hash_password, password)

    def gen_token(self, expire=600):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], expires_in=expire)
        token = s.dumps({'email': self.email})
        return token.decode('utf-8')

    @staticmethod
    def parse_token(token):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return {}
        return data

    def reset_password(self, new_password):
        with db.auto_commit():
            self.password = new_password

        return True

    def confirm(self):
        with db.auto_commit():
            self.confirmed = True


class Goods(Base):
    __abstract__ = True
    launched = Column(Boolean, default=False)
    isbn = Column(String(15), nullable=False, unique=True)
    # user = relationship('User')
    # uid = Column(Integer, ForeignKey('users.id'))

    # book = relationship('Book')
    # bid = Column(Integer, ForeignKey('books.id'))

    @declared_attr
    def user(cls):
        return relationship('User')

    @declared_attr
    def uid(cls):
        return Column(Integer, ForeignKey('users.id'))

    @declared_attr
    def book(cls):
        return relationship('Book')

    @declared_attr
    def bid(cls):
        return Column(Integer, ForeignKey('books.id'))

    @classmethod
    def get_book_goods(cls, bid, uid=None):
        if uid is not None:
            return cls.query.filter_by(uid=uid, bid=bid, launched=False).all()
        return cls.query.filter_by(bid=bid, launched=False).all()

    @classmethod
    def get_user_goods(cls, uid=None):
        return cls.query.filter_by(uid=uid, launched=False).order_by(desc(cls.create_time)).all()

    @staticmethod
    def get_goods_counts(target_cls, isbn_lst):
        count_lst = db.session.query(func.count(target_cls.id), target_cls.isbn).filter(
            target_cls.launched==False, target_cls.isbn.in_(isbn_lst), target_cls.status==True
        ).group_by(target_cls.isbn).all()

        return [EachGoodsCount(element[0], element[1]) for element in count_lst]

    @classmethod
    def save_goods(cls, check_cls, isbn, bid, uid):
        if check_cls.query.filter_by(bid=bid, uid=uid, launched=False).first():
            if check_cls.__name__ == Gift.__name__:
                flash('这本书已经在你的赠送清单中')
            else:
                flash('这本书已经在你的心愿清单中')
        else:
            goods = cls.query.filter_by(use_base=True, bid=bid, uid=uid, launched=False).first()
            if goods:
                goods.change_status()
            else:
                goods = cls()
                goods.isbn = isbn
                goods.bid = bid
                goods.uid = uid
            with db.auto_commit():
                if check_cls.__name__ == Gift.__name__:
                    current_user.beans += current_app.config['BEANS_UPLOAD_ONE_BOOK']
                db.session.add(goods)


class Gift(Goods):
    __tablename__ = 'gifts'

    @classmethod
    def recent(cls):
        return cls.query.filter_by(launched=False).group_by(cls.id).order_by(desc(cls.create_time)).limit(
            current_app.config['RECENT_BOOK_COUNT']).distinct().all()


class Wish(Goods):
    __tablename__ = 'wishes'


class Drift(Base):
    id = Column(Integer, primary_key=True)

    # 邮寄信息
    recipient_name = Column(String(20), nullable=False)
    address = Column(String(100), nullable=False)
    mobile = Column(String(20), nullable=False)
    message = Column(String(200))

    # 书籍信息
    book_isbn = Column(String(13))
    book_title = Column(String(50))
    book_author = Column(String(30))
    book_img = Column(String(50))

    # 请求者信息
    requester_id = Column(Integer)
    requester_nickname = Column(String(20))

    # 赠送者信息
    presenter_id = Column(Integer)
    gift_id = Column(Integer)
    presenter_nickname = Column(String(20))

    _pending = Column('pending', SmallInteger, default=1)

    @property
    def pending(self):
        return PendingStatus(self._pending)

    @pending.setter
    def pending(self, status):
        self._pending = status.value


@login_manager.user_loader
def get_user(uid):
    return User.query.get(int(uid))
