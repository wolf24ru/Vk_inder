import random
import vk_api
import Sicret_deta
from VK_class import VK_bot
from VKinder_db import VKinder_db

# Подключение к ВК
TOKEN_VK_GROUP = Sicret_deta.TOKEN_VK_GROUP
SERVICE_KEY = Sicret_deta.SERVICE_KEY
USER_TOKEN = Sicret_deta.USER_TOKEN


# Подключение к БД
BD_USER = 'vk'
USER_PASSWORD = '12345678'
BD_NAME = 'vkinder_db'


def person_find(vk_connect, db_connect, user_id: int, request_obj) -> dict:
    """
        Функция для нахождения человека по заданным характеристикам
        :param vk_connect: Объект vk_api
        :param db_connect: Объект sqlalchemy для соединения с БД
        :param user_id: id пользователя с котором идет переписка
        :param request_obj: объект базы данных(sqlalchemy.qery) с данными последнего запроса
        :return: Словарь с данными найденного пользователя
    """
    print('start find')
    try:
        search_users = vk_connect.user_session.get_api().users.search(
            count=1000,
            city=vk_connect.search_city_id(request_obj.city),
            country=1,
            age_from=request_obj.age_from,
            age_to=request_obj.age_to,
            sex=request_obj.sex,
            status=request_obj.marital_status,
            fields='domain'
        )['items']
    except AttributeError:
        return None
    # из полученного списка рандомно выбрать  человека
    user_for_you = random.choice(search_users)
    if not db_connect.check_user_search(user_for_you['id'], user_id):
        # Получить 3 фото удовлетворяющие запросу

        try:
            photos_user_all = vk_connect.user_session.get_api().photos.get(
                owner_id=user_for_you['id'],
                album_id='profile',
                extended=1,
                count=100,
            )['items']
        except vk_api.exceptions.ApiError:
            return person_find(vk_connect, db_connect, user_id, request_obj)
        photo_list = [link for link in
                      sorted(photos_user_all, key=lambda item: (item['likes']['count'], item['comments']['count']),
                             reverse=True)[:3]]
        # получить ссылку
        # сообщение с человеком, сообщение с топ-3 фото
        url_profile = f'https://vk.com/{user_for_you["domain"]}'
        profile = f'@{user_for_you["domain"]}({user_for_you["first_name"]})'
        vk_connect.send_msg(f'Я нашел для тебя {profile}',
                            user_id,
                            vk_connect.keyboard_old_find.get_keyboard()
                            )

        for photo in photo_list:
            vk_connect.send_photo(user_id, photo)
        # vk_connect.keyboard_find()
        person = {
            'person_id': user_for_you['id'],
            'user_name': user_for_you["first_name"],
            'url_profile': url_profile,
            'photo_list': photo_list
        }
        return person
    else:
        return person_find(vk_connect, user_id, request_obj, )


def start(event, user_name: str, vk_connect, db_connect) -> object:
    """
    Начало общения
    :param event: Объект vk_api
    :param user_name: имя пользователя
    :param vk_connect: Объект vk_api
    :param db_connect: Объект sqlalchemy для соединения с БД
    :return: объект БД с последним запросом пользователя
    """
    # take_token(vk_connect, event.user_id)
    # проверка на нового пользователя
    # если пользователь новый
    if db_connect.check_new_user(event.user_id, user_name):
        vk_connect.send_msg(message=f'Отлично! {user_name}, ну что попробуем найти тебе пару?\n'
                                    f'Для начала давай настроим поиск!',
                            user_id=event.user_id
                            )
        request_dict = vk_connect.new_user_search(event.user_id)
        #     варианты кнопок: "все верно, начать поиск" "изменить запрос"
        db_connect.add_request(event.user_id,
                               request_dict['age_from'],
                               request_dict['age_to'],
                               request_dict['sex'],
                               request_dict['city'],
                               request_dict['marital_status'])
        vk_connect.send_msg(message=f'Ну а теперь мы можем попытаться найти того кто покорит твоё сердце!\n'
                                    f'Жмякай кнопку "Поиск" и приступим',
                            user_id=event.user_id,
                            keyboard=vk_connect.keyboard_old.get_keyboard()
                            )
    # Если пользователь уже есть в базе
    else:
        vk_connect.send_msg(message=f'Рад тебя снова видеть, {user_name}.\n'
                                    f'Ну что попробуем найти тебе пару?',
                            user_id=event.user_id,
                            keyboard=vk_connect.keyboard_old.get_keyboard()
                            )
        # проверка на наличе запроса от пользователя
    return db_connect.last_request(event.user_id)


def cheng_settings(user_id: int, vk_connect, db_connect):
    """
    Изменения настроек
    :param user_id:  Идентификатор пользователя.
    :param vk_connect: Объект vk_api
    :param db_connect: Объект sqlalchemy для соединения с БД
    """
    request_dict = {
        'sex': int,
        'age_from': int,
        'age_to': int,
        'city': str,
        'marital_status': int
    }
    # получаем последний запрос
    request_object = db_connect.last_request(user_id)
    request_dict['age_from'] = request_object.age_from,
    request_dict['age_to'] = request_object.age_to,
    request_dict['sex'] = request_object.sex,
    request_dict['marital_status'] = request_object.marital_status
    request_dict['city'] = request_object.city
    while True:
        listen_list = vk_connect.listen_dialog()
        user_info = listen_list[0]
        event = listen_list[1]
        # user_name = user_info[0]['first_name']

        # меняем локально
        if event.text == 'Изменить возраст' and event.from_user:
            age = vk_connect.cheng_age(event.user_id)
            if age is not None:
                request_dict['age_to'] = age[0]
                request_dict['age_to'] = age[1]
            else:
                vk_connect.wrong_input(event.user_id)
                vk_connect.keyboard_settings.get_keyboard()
        elif event.text == 'Изменить пол' and event.from_user:
            sex = vk_connect.cheng_sex(event.user_id)
            request_dict['sex'] = sex
        elif event.text == 'Изменить город' and event.from_user:
            while True:
                city = vk_connect.cheng_city(event.user_id)
                if vk_connect.check_city(city, event.user_id):
                    request_dict['city'] = city
                    break
        elif event.text == 'Изменить положение' and event.from_user:
            marital_status = vk_connect.cheng_status(event.user_id)
            request_dict['marital_status'] = marital_status
        # по нажатию записывать все в базу
        elif event.text == 'Всё верно' and event.from_user:
            db_connect.add_request(event.user_id,
                                   request_dict['age_from'],
                                   request_dict['age_to'],
                                   request_dict['sex'],
                                   request_dict['city'],
                                   request_dict['marital_status'],
                                   )
            vk_connect.msg_settings_save(event.user_id)
            return
        # Удалить все об пользователи
        elif event.text == 'Удалить всё об о мне' and event.from_user:
            # Реализовать удаление из базы всей информации о пользователе
            db_connect.delete_all(event.user_id)
            vk_connect.send_msg('Это было весело, что же, прощай!',
                                event.user_id,
                                keyboard=vk_connect.keyboard_new.get_keyboard())
            return
        else:
            vk_connect.i_not_understand(event.user_id)
        vk_connect.msg_setting_remember(event.user_id)


def main_logic(prog_status, vk_connect, db_connect):
    """
    Главная логика бота(в основном необходима что бы не засорять код)
    :param prog_status: Статус выполнения программы
    :param vk_connect: Объект vk_api
    :param db_connect: Объект sqlalchemy для соединения с БД
    """
    while True:
        listen_list = vk_connect.listen_dialog()
        user_info = listen_list[0]
        event = listen_list[1]
        user_name = user_info[0]['first_name']
        # обработка сбоя
        if not prog_status:
            vk_connect.not_understand_msg(event.user_id)
        # Начало
        if event.text == 'Начать' and event.from_user:
            start(event, user_name, vk_connect, db_connect)
        elif event.text == 'Поиск' and event.from_user:
            request_object = db_connect.last_request(event.user_id)
            if request_object:
                # Выполнить поиск по старым запросам
                person = person_find(vk_connect, db_connect, event.user_id, request_object)
                if person:
                    db_connect.add_search(
                        person['person_id'],
                        event.user_id,
                        person['user_name']
                    )
                    # vk_connect.send_msg('', event.user_id, vk_connect.keyboard_old_find.get_keyboard())
                else:
                    start(event, user_name, vk_connect, db_connect)
                # vk_connect.msg_settings_save(event.user_id)
            else:
                vk_connect.send_msg(message=f'Я тут заметил что у тебя не настроен фильтр поиска.\n'
                                            f'Давай изменим это!',
                                    user_id=event.user_id
                                    )
                request_dict = vk_connect.new_user_search(event.user_id)
                db_connect.add_request(
                    event.user_id,
                    request_dict['age_from'],
                    request_dict['age_to'],
                    request_dict['sex'],
                    request_dict['city'],
                    request_dict['marital_status']
                )
                vk_connect.msg_settings_save(event.user_id)
        elif event.text == 'Изменить запрос' and event.from_user:
            vk_connect.send_msg(message='Что меняем?',
                                user_id=event.user_id,
                                keyboard=vk_connect.keyboard_settings.get_keyboard())
            cheng_settings(event.user_id, vk_connect, db_connect)
        elif event.text == 'Добавить в избранное' and event.from_user:
            db_connect.add_favorite(event.user_id)
        elif event.text == 'Показать избранное' and event.from_user:
            db_list = db_connect.show_favorite(event.user_id)
            vk_connect.shove_favorite(db_list, event.user_id)
        else:
            vk_connect.i_not_understand(event.user_id)



if __name__ == '__main__':
    # Подключение к VK
    vk_connect = VK_bot(USER_TOKEN, TOKEN_VK_GROUP, SERVICE_KEY)

    # Подключение к БД
    db_connect = VKinder_db(BD_USER, USER_PASSWORD, BD_NAME)

    request_dict = object
    prog_status = 1
    try:
        main_logic(prog_status, vk_connect, db_connect)
    except AttributeError:
        prog_status = 0
        main_logic(prog_status, vk_connect, db_connect)
    except:
        prog_status = 0
        main_logic(prog_status, vk_connect, db_connect)
