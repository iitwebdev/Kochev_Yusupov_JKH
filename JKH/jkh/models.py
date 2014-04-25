#coding: utf-8
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import md5
import random
import string  # pylint: disable=W0402

from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)
from pyramid.threadlocal import get_current_request
from pyramid.events import subscriber, NewRequest



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


class Country(Base):
    __tablename__ = "country"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))


class Region(Base):
    __tablename__ = "region"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))


class Service(Base):
    __tablename__ = "service"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))


class Tarif(Base):
    __tablename__ = "tarif"

    id = Column(Integer, primary_key=True)

    country_id = Column(Integer, ForeignKey("country.id"), nullable=False)
    region_id = Column(Integer, ForeignKey("region.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("service.id"), nullable=False)
    price = Column()


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
        print(user)
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


def send_email(email, password, theme):
    """
    :param email: ПЯ на который будем отправлять письмо
    :param password: пароль пользователя
    :param theme: переменная, по которой понимаем для чего письмо(либо письмо при регистрации или письмо с новым паролем)
    """
    me = 'jkhsup@mail.ru'
    server = 'smtp.mail.ru'
    port = 25
    user_name = 'jkhsup@mail.ru'
    user_password = '123456789w'  #пароль отправителя
    msg = MIMEMultipart()
    msg['From'] = me
    msg['To'] = email
    if theme == 1:
        msg['Subject'] = 'Регистрация на ЖКХ'
        msg_text = MIMEText(
            u'Спасибо за регистрацию на сайте !\n\nВаш логин: '
            + email + u'\n\nВаш пароль: ' + password,
            "plain",
            "utf-8")
        msg.attach(msg_text)
    if theme == 2:
        msg['Subject'] = 'Восстановление пароля на ЖКХ'
        msg_text = MIMEText(u'\nВаш новый пароль: ' + password, "plain", "utf-8")
        msg.attach(msg_text)
    if theme == 3:
        msg['Subject'] = 'Смена пароля на ЖКХ'
        msg_text = MIMEText(u'\nВаш новый пароль: ' + password, "plain", "utf-8")
        msg.attach(msg_text)
    # Подключение
    s = smtplib.SMTP(server, port)
    s.ehlo()
    s.starttls()
    s.ehlo()
    # Авторизация
    s.login(user_name, user_password)
    # Отправка пиьма
    s.sendmail(user_name, email, msg.as_string())
    s.quit()
