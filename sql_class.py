import sqlalchemy as sq
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy_utils import database_exists, create_database,drop_database
from sqlalchemy.dialects.postgresql import insert

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String, nullable=False)

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

    def add_data(self, table_name, data_list):
        table_name_dict = {
            'User': User,
            'Photo': Photo,
            'User_viewer': UserView
        }
        self.session.execute(insert(table_name_dict[table_name])
                        .values(data_list)
                        .on_conflict_do_nothing())
        self.session.commit()

    def check_user_list(self, user_id):
        query_user_list = self.session.query(UserView.viewed_id).filter(UserView.viewer_id == user_id)
        user_list = [ul[0] for ul in query_user_list]
        return user_list

    def check_user(self, user_id):
        query_user = self.session.query(UserView.viewer_id).filter(UserView.viewer_id == user_id).distinct()
        user = query_user[0][0]
        return user
