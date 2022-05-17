import sqlalchemy as sq
from sqlalchemy import UniqueConstraint, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlalchemy.dialects.postgresql import insert

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String, nullable=False)


class Photo(Base):
    __tablename__ = 'photo'

    id = sq.Column(sq.Integer, primary_key=True)
    likes = sq.Column(sq.Integer)
    url_photo = sq.Column(sq.String, nullable=False)
    like = sq.Column(sq.Boolean)
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

    # создание базы
    def create_database(self):
        if not database_exists(self.engine.url):
            create_database(self.engine.url)

    # создание таблиц
    def create_database_tables(self):
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        Base.metadata.create_all(self.engine)

    # удаление базы
    def _drop_database(self):
        if database_exists(self.engine.url):
            drop_database(self.engine.url)

    # метод добавления данных по пользователю в базу
    def add_user(self, data_dict):
        self.session.execute(insert(User)
                             .values(data_dict)
                             .on_conflict_do_update(constraint='user_pkey', set_=data_dict))
        self.session.commit()

    # добавление фотографий в базу
    def add_user_photos(self, photo_list):
        for photo in photo_list:
            self.session.execute(insert(Photo).values(photo).on_conflict_do_nothing())
        self.session.commit()

    # добавление данных по просмотру анкеты
    def add_user_viewer(self, data_dict):
        self.session.execute(insert(UserView).values(data_dict).on_conflict_do_nothing())
        self.session.commit()

    # обновление данных по просмотру анкеты
    def udate_user_viewer(self, data_dict):
        self.session.execute(insert(UserView).values(data_dict).on_conflict_do_update(
            constraint='user_view_viewer_id_viewed_id_key',
            set_={'reaction': data_dict['reaction']}))
        self.session.commit()

    # запрос данных по просмотренным кандидатам из базы
    def check_user_list(self, user_id):
        query_user_list = self.session.query(UserView.viewed_id).filter(UserView.viewer_id == user_id)
        user_list = [ul[0] for ul in query_user_list]
        return user_list

    # проверки наличия данных пользователя в базе
    def check_user(self, user_id):
        query_user = list(self.session.query(UserView.viewer_id).filter(UserView.viewer_id == user_id).distinct())
        return query_user

    #отбор списка избранных
    def select_like_list(self, user_id):
        query_like_list = self.session.query(UserView.viewed_id).filter(UserView.viewer_id == user_id,
                                                                        UserView.reaction == 2)
        user_list = [str(ul[0]) for ul in query_like_list]
        return ','.join(user_list)

