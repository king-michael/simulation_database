from bcrypt import gensalt, hashpw
# from flask_login import UserMixin
from sqlalchemy import Binary, Column, Integer, String

from app import db


# class User(db.Model, UserMixin):
#
#     __tablename__ = 'User'
#
#     id = Column(Integer, primary_key=True)
#     username = Column(String, unique=True)
#     email = Column(String, unique=True)
#     password = Column(Binary)
#
#     def __init__(self, **kwargs):
#         for property, value in kwargs.items():
#             # depending on whether value is an iterable or not, we must
#             # unpack it's value (when **kwargs is request.form, some values
#             # will be a 1-element list)
#             if hasattr(value, '__iter__') and not isinstance(value, str):
#                 # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
#                 value = value[0]
#             if property == 'password':
#                 value = hashpw(value.encode('utf8'), gensalt())
#             setattr(self, property, value)
#
#     def __repr__(self):
#         return str(self.username)

class Database(db.Model):

    __tablename__ = 'Database'

    id = Column(Integer(), primary_key=True)
    name = Column(String(50), nullable=False)
    path = Column(String(250), nullable=False)
    comment = Column(String(250), nullable=True)


    def __repr__(self):
        return """{}(name='{}', path='{}'""".format(
            self.__class__.__name__,
            self.name,
            self.path)

# @login_manager.user_loader
# def user_loader(id):
#     return User.query.filter_by(id=id).first()
#
#
# @login_manager.request_loader
# def request_loader(request):
#     username = request.form.get('username')
#     user = User.query.filter_by(username=username).first()
#     return user if user else None