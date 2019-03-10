from sqlalchemy import Binary, Column, Integer, String
from app import db


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

