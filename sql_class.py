import sqlalchemy as sq
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy_utils import database_exists, create_database,drop_database

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String, nullable=False)
    # url_profile = sq.Column(sq.String, nullable=False)

class Photo(Base):
    __tablename__ = 'photo'

    id = sq.Column(sq.Integer, primary_key=True)
    url_photo = sq.Column(sq.String, nullable=False)
    likes = sq.Column(sq.Integer)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('user.id', ondelete='CASCADE'))

class UserView(Base):
    __tablename__ = 'user_view'

    id = sq.Column(sq.Integer, primary_key=True)
    reaction = sq.Column(sq.Integer, nullable=False)
    viewer_id = sq.Column(sq.Integer, sq.ForeignKey('user.id', ondelete='CASCADE'))
    viewed_id = sq.Column(sq.Integer, sq.ForeignKey('user.id', ondelete='CASCADE'))
    __table_args__ = (UniqueConstraint('viewer_id', 'viewed_id'),)

class VkinderDB:

    def __init__(self, login, password, name):
        self.login = login
        self.password = password
        self.name = name
        self.engine = sq.create_engine(f'postgresql://{self.login}:{password}@localhost/{name}')

    def create_database(self):
        if not database_exists(self.engine.url):
            create_database(self.engine.url)

    def create_database_tables(self):
            self.Session = sessionmaker(bind=self.engine)
            self.session = self.Session()
            Base.metadata.create_all(self.engine)

    def _drop_database(self):
        if database_exists(self.engine.url):
            drop_database(self.engine.url)
            print('таблица удалена')

    def add_users(self, users):
        self.users = []
        for user in self.users:
            self.user_list.append(User(users['id'], users['name']))
            self.session.add_all(self.users)
            self.session.commit()
