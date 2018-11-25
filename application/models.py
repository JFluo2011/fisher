from contextlib import contextmanager
from datetime import datetime
from collections import namedtuple

from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, SmallInteger, desc, func
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy, BaseQuery
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_login import LoginManager
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer

from .libs.helper import keyword_is_isbn
from .spider.fisher_book import FisherBook


login_manager = LoginManager()
EachGiftWishCount = namedtuple('EachGiftWishCount', 'count, isbn')


class SubSQLALchemy(SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as err:
            self.session.rollback()
            raise err


class SubQuery(BaseQuery):
    def filter_by(self, **kwargs):
        if 'status' not in kwargs.keys():
            kwargs.update({'status': 1})
        return super().filter_by(**kwargs)


db = SubSQLALchemy(query_class=SubQuery)


class Base(db.Model):
    __abstract__ = True
    create_time = Column('create_time', Integer)
    status = Column(SmallInteger, default=1)

    def __init__(self):
        self.create_time = int(datetime.now().timestamp())

    def set_attrs(self, attr_dct):
        for key, value in attr_dct.items():
            if (not hasattr(self, key)) or (key == 'id'):
                continue
            setattr(self, key, value)

    def get_format_create_time(self):
        if self.create_time:
            return datetime.fromtimestamp(self.create_time)


class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50), nullable=False)
    summary = Column(String(50))
    author = Column(String(30), default='佚名')
    publisher = Column(String(50))
    price = Column(String(50))
    pages = Column(String(50))
    pubdate = Column(String(1000))
    isbn = Column(String(15), nullable=False, unique=True)
    binding = Column(String(20))
    image = Column(String(50))


class User(UserMixin, Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
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

    @property
    def password(self):
        return self._hash_password
        # raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self._hash_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._hash_password, password)

    def can_save_to_list(self, isbn):
        if not keyword_is_isbn(isbn):
            return False
        book = FisherBook()
        book.search_by_isbn(isbn)
        if not book.first:
            return False
        gift = Gift.query.filter_by(uid=self.id, isbn=isbn, launched=False).first()
        wish = Wish.query.filter_by(uid=self.id, isbn=isbn, launched=False).first()
        if not gift and not wish:
            return True
        else:
            return False

    def gen_token(self, expire=600):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], expires_in=expire)
        token = s.dumps({'id': self.id})
        return token.decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False

        uid = data['id']
        with db.auto_commit():
            user = User.query.get(uid)
            if user is None:
                return False

            user.password = new_password

        return True


class Gift(Base):
    __tablename__ = 'gifts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    launched = Column(Boolean, default=False)
    user = relationship('User')
    beans = relationship('User')
    uid = Column(Integer, ForeignKey('users.id'))
    # 目前都是请求的api，数据库中并没有值，所以直接用isbn来关联，而不是外键
    isbn = Column(String(15), nullable=False)

    # book = relationship('User')
    # bid = Column(Integer, ForeignKey('books.id'))

    @property
    def book(self):
        fisher_book = FisherBook()
        fisher_book.search_by_isbn(self.isbn)
        return fisher_book.first

    @classmethod
    def get_book_gifts(cls, isbn, uid=None):
        if uid is not None:
            return cls.query.filter_by(uid=uid, isbn=isbn, launched=False).all()
        return cls.query.filter_by(isbn=isbn, launched=False).all()

    @classmethod
    def recent(cls):
        return cls.query.filter_by(launched=False).group_by(cls.isbn, cls.id).order_by(desc(cls.create_time)).limit(
            current_app.config['RECENT_BOOK_COUNT']).distinct().all()

    @classmethod
    def get_user_gifts(cls, uid):
        return cls.query.filter_by(uid=uid, launched=False).order_by(desc(cls.create_time)).all()

    @classmethod
    def get_wish_counts(cls, isbn_lst):
        count_lst = db.session.query(func.count(Wish.id), Wish.isbn).filter(
            Wish.launched == False, Wish.isbn.in_(isbn_lst), Wish.status == 1).group_by(Wish.isbn).all()

        return [EachGiftWishCount(element[0], element[1]) for element in count_lst]


class Wish(Base):
    __tablename__ = 'wishes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    launched = Column(Boolean, default=False)
    user = relationship('User')
    uid = Column(Integer, ForeignKey('users.id'))
    # 目前都是请求的api，数据库中并没有值，所以直接用isbn来关联，而不是外键
    isbn = Column(String(15), nullable=False)

    # book = relationship('User')
    # bid = Column(Integer, ForeignKey('books.id'))

    @property
    def book(self):
        fisher_book = FisherBook()
        fisher_book.search_by_isbn(self.isbn)
        return fisher_book.first

    @classmethod
    def get_book_wishes(cls, isbn, uid=None):
        if uid is not None:
            return cls.query.filter_by(uid=uid, isbn=isbn, launched=False).all()
        return cls.query.filter_by(isbn=isbn, launched=False).all()

    @classmethod
    def get_user_wishes(cls, uid):
        return cls.query.filter_by(uid=uid, launched=False).order_by(desc(cls.create_time)).all()

    @classmethod
    def get_gift_counts(cls, isbn_lst):
        count_lst = db.session.query(func.count(Gift.id), Gift.isbn).filter(
            Gift.launched == False, Gift.isbn.in_(isbn_lst), Gift.status == 1).group_by(Gift.isbn).all()

        return [EachGiftWishCount(element[0], element[1]) for element in count_lst]


@login_manager.user_loader
def get_user(uid):
    return User.query.get(int(uid))
