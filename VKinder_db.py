import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class User_table(Base):
    __tablename__ = 'user_table'

    id_user = sq.Column(sq.Integer, primary_key=True)
    name_user = sq.Column(sq.String(40))


class Marital_Status(Base):
    __tablename__ = 'marital_status'

    id_status = sq.Column(sq.Integer, primary_key=True)
    marital_status = sq.Column(sq.String)


class User_request(Base):
    __tablename__ = 'user_request'

    request_id = sq.Column(sq.Integer, nullable=False)
    id_user = sq.Column(sq.Integer, sq.ForeignKey('user_table.id_user'))
    age_from = sq.Column(sq.Integer, nullable=False)
    age_to = sq.Column(sq.Integer, nullable=False)
    sex = sq.Column(sq.Integer, sq.CheckConstraint('sex>=0 and sex<=2'), nullable=False)
    city = sq.Column(sq.String, nullable=False)
    marital_status = sq.Column(sq.Integer, sq.ForeignKey('marital_status.id_status'))
    sq.PrimaryKeyConstraint(request_id, id_user, name='user_request_pk')


class Search_users(Base):
    __tablename__ = 'search_users'

    id_search = sq.Column(sq.Integer, nullable=False)
    search_user_id = sq.Column(sq.Integer, nullable=False)
    search_user_name = sq.Column(sq.String, nullable=False)
    to_id_user = sq.Column(sq.Integer, sq.ForeignKey('user_table.id_user'))
    favorite = sq.Column(sq.Boolean, default=False)
    # age = sq.Column(sq.Integer, nullable=False)
    # sex = sq.Column(sq.Integer, nullable=False)
    # city = sq.Column(sq.String, nullable=False)
    # marital_status = sq.Column(sq.Integer, sq.ForeignKey('marital_status.id_status'))
    sq.PrimaryKeyConstraint(id_search, search_user_id, name='search_users_pk')


class VKinder_db:

    def __init__(self, user: str, password: str, db: str, port=5432):
        """
        Подключение к БД
        :param user: Имя пользователя БД
        :param password: Пароль пользователя БД
        :param db: Имя БД
        :param port: Порт подключения (по умолчанию 5432)
        """

        engine = sq.create_engine(f'postgresql://{user}:{password}@localhost:{port}/{db}')
        Session = sessionmaker(bind=engine)
        self.sess = Session()
        Base.metadata.create_all(engine)

        if not self.sess.query(Marital_Status).all():
            self.sess.add_all([
                Marital_Status(marital_status='не женат (не замужем)'),
                Marital_Status(marital_status='встречается'),
                Marital_Status(marital_status='помолвлен(-а)'),
                Marital_Status(marital_status='женат (замужем)'),
                Marital_Status(marital_status='всё сложно'),
                Marital_Status(marital_status='в активном поиске'),
                Marital_Status(marital_status='влюблен(-а)'),
                Marital_Status(marital_status='в гражданском браке'),
            ])
            self.sess.commit()

    def add_request(self, id_user: int, age_from: int, age_to: int, sex: int, city: str, marital_status: int):
        """
        Добавление нового запроса
        :param id_user: Идентификатор пользователя, соответствует id в ВК
        :param age_from: Левая граница возраста
        :param age_to: Правая граница возраста
        :param sex: Пол
        :param city: Город
        :param marital_status: Семейное положение
        """
        request_id = 1
        query = self.sess.query(User_request).all()
        if query:
            request_id += query[-1].request_id
        self.sess.add(User_request(request_id=request_id,
                                   id_user=id_user,
                                   age_from=age_from,
                                   age_to=age_to,
                                   sex=sex,
                                   city=city,
                                   marital_status=marital_status))
        self.sess.commit()

    def add_favorite(self, user_id: str):
        """
        Добавление в избранное
        :param user_id: Идентификатор пользователя, соответствует id в ВК
        """
        last_find_user = self.sess.query(Search_users) \
            .where(Search_users.to_id_user == int(user_id)).all()
        last_find_user[-1].favorite = True
        self.sess.commit()

    def show_favorite(self, user_id: str) -> object:
        """
        Вывод списка избранных
        :param user_id: Идентификатор пользователя, соответствует id в ВК
        :return:список всех объектов содержащих favorite = True
        """
        all_favorite = self.sess.query(Search_users) \
            .where(Search_users.favorite == True) \
            .where(Search_users.to_id_user == int(user_id)).all()
        return all_favorite

    def add_user(self, id_user: int, name_user: str):
        """
        Добавление нового пользователя в БД
        :param id_user: Идентификатор пользователя, соответствует id в ВК
        :param name_user: Имя пользователя
        """
        self.sess.add(User_table(id_user=id_user, name_user=name_user))
        self.sess.commit()

    # 	добавление пользователя из результата запроса
    def add_search(self, search_user_id: int, to_id_user: int, search_user_name: str):
        """
        Добавление информации о найденном человеке, что бы его больше е выкидывало в поиск:
        :param search_user_id: Идентификатор найденного пользователя, соответствует id в ВК
        :param to_id_user: Идентификатор пользователя от которого происходит запрос, соответствует id в ВК
        """
        id_search = 1
        query = self.sess.query(Search_users).all()
        if query:
            id_search += query[-1].id_search
        self.sess.add(Search_users(id_search=id_search,
                                   search_user_id=search_user_id,
                                   to_id_user=to_id_user,
                                   search_user_name=search_user_name
                                   ))
        self.sess.commit()

    def delete_request(self, user_id):
        """
        Удаление запроса
        в сатии реализации
        """
        self.sess.query(User_request)\
            .filter(User_request.id_user == user_id)\
            .delete(synchronize_session="evaluate")

    def delete_user(self, user_id):
        """
        Удаление пользователя
        в сатии реализации
        """
        self.sess.query(User_table)\
            .filter(User_table.id_user == user_id)\
            .delete(synchronize_session="evaluate")

    def delete_search(self, user_id):
        """
        Удаление результата запроса
        в сатии реализации
        """
        self.sess.query(Search_users)\
            .filter(Search_users.to_id_user == user_id)\
            .delete(synchronize_session="evaluate")

    def delete_all(self, user_id):
        self.delete_request(user_id)
        self.delete_search(user_id)
        self.delete_user(user_id)

    def check_new_user(self, user_id: int, user_name: str) -> bool:
        """
        Проверка на "нового пользователя". Проверяет есть ли пользователь от которого осуществляется запрос в БД
        И добавление его в БД если его там нет
        :param user_id: Идентификатор пользователя, соответствует id в ВК
        :param user_name: Имя пользователя
        :return: True - если пользователь новый; False - если пользователь уже есть в БД.
        """
        query = self.sess.query(User_table)
        for id_u in query:
            if user_id == id_u.id_user:
                return False
        self.add_user(user_id, user_name)
        return True

    def check_user_search(self, person_id: int,  user_id: int) -> bool:
        """
        Проверка на выдачу конкретного найденного человека
        :param person_id: Идентификатор найденного человека
        :return: True - Пользователь ранее был найден; False - Пользователя еще нет в БД
        """
        query = self.sess.query(Search_users) \
            .where(Search_users.search_user_id == int(person_id)) \
            .where(Search_users.to_id_user == int(user_id)).all()
        if query:
            return True
        return False

    # Проверка на наличе запроса от пользователя в БД
    #   Выдача последнего запроса пользователя
    def last_request(self, user_id: int) -> dict:
        """
        Проверка на наличе запроса от пользователя в БД; Выдача последнего запроса пользователя;
        :param user_id: Идентификатор пользователя
        :return: Последний запрос пользователя
        """
        query = self.sess.query(User_request).where(User_request.id_user == int(user_id)).all()
        if query:
            return query[-1]
        return query
