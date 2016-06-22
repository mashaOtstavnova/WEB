#coding: utf-8

import random
import string  # pylint: disable=W0402
import hashlib
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import  String,  ForeignKey, Date, Numeric
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship)

from pyramid.threadlocal import get_current_request
from sqlalchemy import (
    Column,
    Integer,
    Text,
)
Base = declarative_base()
DBSession = scoped_session(sessionmaker(), scopefunc=get_current_request)
Base = declarative_base()


def rndstr(length=32):
    chars = string.ascii_letters + string.digits
    return ''.join(
        random.choice(chars) for x in range(length))

class Country(Base):
    __tablename__ = "country"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    def __repr__(self):
        return self.name


class Region(Base):
    __tablename__ = "region"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    country_id = Column(Integer, ForeignKey("country.id"), nullable=False)
    country = relationship("Country")

    def __repr__(self):
        return self.name


class City(Base):
    __tablename__ = "city"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    region_id = Column(Integer, ForeignKey("region.id"), nullable=False)
    region = relationship("Region")

    def __repr__(self):
        return self.name


class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User")
    advert_id = Column(Integer, ForeignKey("advert.id"), nullable=False)
    advert = relationship("Advert")
    patchImageAvatar = Column(Text)

    def __repr__(self):
        return self.id

class Advert(Base):
    __tablename__ = "advert"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    text = Column(Text)
    date = Column(Date)
    cost = Column(Numeric(10, 2))
    def __repr__(self):
        return self.name

class ProfilePic(Base):
    __tablename__ = "profilePic"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User")
    name = Column(String(255))
    patchImageAvatar = Column(Text)

    def __repr__(self):
        return self.name

class User(Base):
    __tablename__ = "user"
    _password = None

    id = Column(Integer, primary_key=True)

    name = Column(String(255))
    email = Column(String(50))
    phone = Column(String(50))
    city_id = Column(Integer, ForeignKey("city.id"), nullable=True)
    city = relationship("City")

    _salt = Column("salt", String(32))
    hpass = Column(String(32))

    def __repr__(self):
        return self.name

    @hybrid_property
    def salt(self):
        if self._salt:
            return self._salt
        self._salt = rndstr(32)
        return self._salt

    @salt.expression
    def salt(cls):
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
        m = hashlib.md5()
        m.update(pwd.encode())
        m.update(user.salt.encode())
        return m.hexdigest()




def register(name, email, password,phone,city):
    if name and email and password and phone:
        session = DBSession()
        query = session.query(User).filter(User.email == email)
        try:
            query.one()
            return False
        except NoResultFound or MultipleResultsFound:
            # Создаем нового пользователя
            Base.metadata.create_all()
            user = User(name=name, email=email)
            user.password = password
            user.phone = phone
            user.city = city
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
