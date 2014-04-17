#coding: utf-8
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, PickleType
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)
from pyramid.threadlocal import get_current_request
from pyramid.events import subscriber, NewRequest
import md5
import random
import string  # pylint: disable=W0402
import socket

# pylint: disable=C0103
Base = declarative_base()
DBSession = scoped_session(sessionmaker(), scopefunc=get_current_request)
Base = declarative_base()
# pylint: enable=C0103


def close_db_connection(request):  # pylint: disable=W0613
    DBSession.remove()


@subscriber(NewRequest)
def register_close_db_connection(event):
    event.request.add_finished_callback(close_db_connection)


def rndstr(length=32):
    chars = string.ascii_letters + string.digits
    return ''.join(
        random.choice(chars) for x in range(length))


class User(Base):
    """ User class for keeping employee info & credentials """

    __tablename__ = "user"
    _password = None

    id = Column(Integer, primary_key=True)

    name = Column(String(255))
    email = Column(String(50))
    _salt = Column("salt", String(32))
    hpass = Column(String(32))

    @hybrid_property
    def salt(self):
        if self._salt:
            return self._salt
        self._salt = rndstr(32)
        return self._salt

    @salt.expression  # pyflakes: disable=W806
    def salt(cls):  # pylint: disable=E0213
        return cls._salt

    @salt.setter
    def salt(self, value):
        self._salt = value

    @property
    def password(self):
        """ Gets a transient password """
        return self._password

    @password.setter
    def password(self, value):
        """ set transient password and updates password
            hash if password is not empty
        """
        if not value:
            return
        self._password = value
        self.hpass = User.get_hashed_password(self)

    def check_password(self, passwd):
        return self.hpass == User.get_hashed_password(self, passwd)

    @staticmethod
    def get_hashed_password(user, pwd=None):
        pwd = pwd or user.password
        if pwd is None:
            raise Exception("Hashed password of None")
        mhash = md5.new()
        mhash.update(pwd)
        mhash.update(user.salt)
        return mhash.hexdigest()


def pas_gen():
    return ''.join(random.choice(
        string.letters + string.digits
    ) for i in range(10))


def register(name, email, password):
    if name and email and password:
        session = DBSession()
        query = session.query(User).filter(User.email == email)
        try:
            query.one()
            #raise EmailExistError(u'Такой почтовый ящик уже существует')
            return False
        except NoResultFound or MultipleResultsFound:
            # Создаем нового пользователя
            user = User(name=name, email=email)
            ##TODO SMTP mail
            user.password = password
            session.add(user)
            session.commit()
            return user
    else:
        return False


def login(email, password):
    """
    Функция проверяет наличие почтового ящика в БД и сверяет пароль
    :param email: ПЯ введенный пользователем
    :param password: пароль введенный пользовытелем
    :return: True - пользователь найден в базе
    """

    session = DBSession()
    query = session.query(User).filter(User.email == email)
    try:
        user = query.one()
        if User.get_hashed_password(user, password) == user.hpass:
            return user
        else:
            return None
    except NoResultFound:
        return None


def all_users():
    session = DBSession()
    for user in session.query(User):
        print user.name, user.email


def del_all():
    session = DBSession
    for user in session.query(User):
        session.delete(user)
    session.commit()