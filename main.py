# Подключение к ВК групе
TOKEN_VK_GROUP = '3205c71e7b40a49f76212f837948cc30732790d54bc5f7c446c458d201ebae6810281418b979888ad9eb0'
GROUP_ID = 207491288

# Подключение к БД
BD_USER = 'vk'
USER_PASSWORD = '12345678'
BD_NAME = 'vkinder_db'
import random
import vk_api
import requests
from VK_class import VK_bot
from VKinder_db import VKinder_db
from urllib.parse import urlparse


def person_find(vk_connect, db_connect, user_id: int, request_dict: object) -> dict:
    # получить человека по заданным параметрам
    try:
        search_users = vk_connect.user_session.get_api().users.search(
            count=1000,
            city=vk_connect.search_city_id(request_dict.city),
            country=1,
            age_from=request_dict.age_from,
            age_to=request_dict.age_to,
            sex=request_dict.sex,
            status=request_dict.marital_status,
            fields='domain'
        )['items']
    except AttributeError:
        return None
    # из полученного списка рендомно выбрать  человека
    user_for_you = random.choice(search_users)
    if not db_connect.check_user_search(user_for_you['id']):
        # Получить 3 фото удовлетворяющие запросу

        try:
            photos_user_all = vk_connect.user_session.get_api().photos.get(
                owner_id=user_for_you['id'],
                album_id='profile',
                extended=1,
                count=100,
            )['items']
        except vk_api.exceptions.ApiError:
            return person_find(vk_connect, db_connect, user_id, request_dict)
        photo_list = [link for link in
                      sorted(photos_user_all, key=lambda item: (item['likes']['count'], item['comments']['count']),
                             reverse=True)[:3]]
        # получить ссылку
        # сообщение с человеком, сообщение с топ-3 фото
        url_profile = f'https://vk.com/{user_for_you["domain"]}'
        profile = f'@{user_for_you["domain"]}({user_for_you["first_name"]})'
        vk_connect.send_msg(message=f'Я нашел для тебя {profile}',
                            user_id=user_id,
                            )

        for photo in photo_list:
            vk_connect.send_photo(user_id, photo)
        vk_connect.keyboard_new.get_keyboard()
        return {
            'person_id': user_for_you['id'],
            'user_name': user_for_you["first_name"],
            'url_profile': url_profile,
            'photo_list': photo_list
        }
    else:
        return person_find(vk_connect, user_id, request_dict)


def take_token(vk_connect: object, id_user: str):
    # Пишет сообщение о том что ему нужен доступ
    vk_connect.send_msg(message=f'Один маленький нюанс. Для полноценнной работы мне нужно твое разершение.\n'
                                f'А так как я чат бот, перенаправлять тебя на другие источники я не могу.\n'
                                f'Так что мне нужна твоя помощь\n'
                                f'\n'
                                f'Для этого перейди по этой ссылке:\n'
                                f'\nhttps://oauth.vk.com/authorize?client_id=7895500&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=pages&response_type=token&v=5.131\n'
                                f'\nСкопируй то что будет в адресной страке и отправь мне\n'
                                f'Я жду!',
                        user_id=id_user
                        )
    url = urlparse(vk_connect.listen_dialog()[1].text)
    params_one = url.fragment.split(';')
    params = [i.split('&')[0] for i in params_one]
    params_dict = {i.split('=')[0]: i.split('=')[1] for i in params}
    if params_dict:
        vk_connect.user_auoth(params_dict['access_token'])


    # и подключается к данными пользваотедля
def start(event: object, user_name: str) -> object: #vk_connect, db_connect):
    take_token(vk_connect, event.user_id)
    # проверка на нового пользователя
    # если пользователь новый
    if db_connect.check_new_user(event.user_id, user_name):
        vk_connect.send_msg(message=f'Отлично! {user_name}, ну что попробуем найти тебе пару?\n'
                                    f'Для начала давай настроим поиск!',
                            user_id=event.user_id
                            )
        request_dict = vk_connect.new_user_search(event.user_id)
        # Отобразить клавиатура с сообщением  'Давай еще раз все проверим'

        #     варианты кнопок: "все верно, начать поиск" "изменить запрос"
        db_connect.add_request(event.user_id,
                               request_dict['age_from'],
                               request_dict['age_to'],
                               request_dict['sex'],
                               request_dict['city'],
                               request_dict['marital_status'])
        vk_connect.send_msg(message=f'Ну а теперь мы можем попытаться найти того кто покорит твое сердце!\n'
                                    f'жмякай кнопку "Поиск" и приступим',
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


def cheng_settings(user_id):
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


        user_name = user_info[0]['first_name']
        # меняем локально
        print('heng settings')
        if event.text == 'Изменить возраст' and event.from_user:
            age = vk_connect.cheng_age(event.user_id)
            if age is not None:
                print('rewrite age')
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
            print('all rathete')
            db_connect.add_request(event.user_id,
                                   request_dict['age_from'],
                                   request_dict['age_to'],
                                   request_dict['sex'],
                                   request_dict['city'],
                                   request_dict['marital_status'],
                                   )
            print('all rathete stop')
            vk_connect.msg_settings_save(event.user_id)
            print('print msg')
            return
        # Удалить все об пользователи
        elif event.text == 'Удалить всё об о мне' and event.from_user:
            # Реализовать удаление из базы всей информации о пользователе
            pass
        else:
            vk_connect.i_not_understand(event.user_id)
        vk_connect.msg_setting_remember(event.user_id)


def main_logic(request_dict: object, prog_status):
    else_msg =[
        'Не понимаю о чем ты!',
        'Что-то на непонятном\n давай попробуем еще раз',
        'Кажется, я не знаю таких команд\n я же всего лишь бот',
        'Воу-воу, полегче. Я всего лишь структурированный код(хотелось бы в это верить)\n',
        'Так, давай вот без этого.',
        'А можно не отклоняться от сценария?\n\n Спасибо...',
        'B и что мне с эти делать?'
    ]
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
            start(event, user_name)
        elif event.text == 'Поиск' and event.from_user:
            request_dict = db_connect.last_request(event.user_id)
            if request_dict:
                # Выполнить поиск по старым запросам
                person = person_find(vk_connect, db_connect, event.user_id, request_dict)
                if person:
                    db_connect.add_search(
                        person['person_id'],
                        event.user_id
                    )
                else:
                    start(event, user_name)
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
                # person = person_find(vk_connect, db_connect, event.user_id, request_dict)

                # начать отсюда. тут надо добавить обработчик поиска и проверку на наличие существующего запроса

        elif event.text == 'Изменить запрос' and event.from_user:
            vk_connect.send_msg(message='Что меняем?',
                                user_id=event.user_id,
                                keyboard=vk_connect.keyboard_settings.get_keyboard())
            cheng_settings(event.user_id)
        else:
            vk_connect.i_not_understand(event.user_id)



if __name__ == '__main__':
    # Подключение к VK
    vk_connect = VK_bot(GROUP_ID, TOKEN_VK_GROUP)

    # Подключение к БД
    db_connect = VKinder_db(BD_USER, USER_PASSWORD, BD_NAME)

    request_dict = object
    prog_status = 1
    try:
        main_logic(request_dict, prog_status)
    except AttributeError:
        prog_status = 0
        main_logic(request_dict, prog_status)
    except:
        prog_status = 0
        main_logic(request_dict, prog_status)
