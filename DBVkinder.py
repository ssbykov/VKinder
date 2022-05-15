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
    url_photo = sq.Column(sq.String, nullable=False)
    likes = sq.Column(sq.Integer)
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
            if self.session.query(Photo.like).filter(Photo.id == int(photo['id'])).first():
                photo['like'] = list(self.session.query(Photo.like).filter(Photo.id == int(photo['id'])).first())[0]
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
        query_user_list = self.session.query(UserView.viewed_id).filter(UserView.viewer_id == user_id,
                                                                        UserView.reaction != 1)
        user_list = [ul[0] for ul in query_user_list]
        return user_list

    # проверки наличия данных пользователя в базе
    def check_user(self, user_id):
        query_user = list(self.session.query(UserView.viewer_id).filter(UserView.viewer_id == user_id).distinct())
        return query_user

    # запрос фото пользователя
    def get_user_photos(self, user_id):
        query_user = list(self.session.query(Photo.id).filter(Photo.user_id == user_id).order_by(Photo.likes.desc()))
        attachment = ''
        for photo in query_user:
            attachment += f"photo{user_id}_{photo['id']},"
        return attachment

    # простановка/удаление лайка фото
    def like_user_photo(self, user_id, photo_like):
        photo_id = list(self.session.query(Photo.id).filter(
            Photo.user_id == user_id).order_by(Photo.likes.desc()))[int(photo_like)-1][0]
        photo = self.session.query(Photo).get(photo_id)
        if photo.like:
            photo.like = False
        else:
            photo.like = True
        self.session.commit()
        return photo_id

