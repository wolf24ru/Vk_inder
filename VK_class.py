import random
import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.upload import VkUpload


class VK_bot:
    def __init__(self, user_token: str, token_vk_group: str, service_key: str):
        self.token_vk_group = token_vk_group
        self.user_token = user_token
        self.vk_session = vk_api.VkApi(token=self.token_vk_group)
        self.user_session = vk_api.VkApi(token=user_token)
        self.photo_upload = VkUpload(self.vk_session)
        self.service_session = vk_api.VkApi(token=service_key)

        self.keyboard_new = VkKeyboard(one_time=False)
        self.keyboard_new.add_button('Начать', color=VkKeyboardColor.POSITIVE)

        self.keyboard_old = VkKeyboard(one_time=False)
        self.keyboard_old.add_button('Поиск', color=VkKeyboardColor.POSITIVE)
        self.keyboard_old.add_line()
        self.keyboard_old.add_button('Изменить запрос', color=VkKeyboardColor.PRIMARY)
        self.keyboard_old.add_button('Показать избранное', color=VkKeyboardColor.POSITIVE)

        self.keyboard_old_find = VkKeyboard(one_time=False)
        self.keyboard_old_find.add_button('Поиск', color=VkKeyboardColor.POSITIVE)
        self.keyboard_old_find.add_button('Изменить запрос', color=VkKeyboardColor.PRIMARY)
        self.keyboard_old_find.add_line()
        self.keyboard_old_find.add_button('Добавить в избранное', color=VkKeyboardColor.POSITIVE)
        self.keyboard_old_find.add_button('Показать избранное', color=VkKeyboardColor.POSITIVE)

        self.keyboard_settings = VkKeyboard(one_time=False)
        self.keyboard_settings.add_button('Изменить возраст', color=VkKeyboardColor.SECONDARY)
        self.keyboard_settings.add_button('Изменить пол', color=VkKeyboardColor.SECONDARY)
        self.keyboard_settings.add_line()
        self.keyboard_settings.add_button('Изменить город', color=VkKeyboardColor.SECONDARY)
        self.keyboard_settings.add_button('Изменить положение', color=VkKeyboardColor.SECONDARY)
        self.keyboard_settings.add_line()
        self.keyboard_settings.add_button('Всё верно', color=VkKeyboardColor.PRIMARY)
        self.keyboard_settings.add_line()
        self.keyboard_settings.add_button('Удалить всё об о мне', color=VkKeyboardColor.NEGATIVE)

        self.keyboard_sex = VkKeyboard(one_time=True)
        self.keyboard_sex.add_button('Мужской', color=VkKeyboardColor.SECONDARY)
        self.keyboard_sex.add_button('Женский', color=VkKeyboardColor.SECONDARY)

        self.keyboard_marital_normal = VkKeyboard(one_time=False)
        self.keyboard_marital_normal.add_button('не женат (не замужем)', color=VkKeyboardColor.SECONDARY)
        self.keyboard_marital_normal.add_button('всё сложно', color=VkKeyboardColor.SECONDARY)
        self.keyboard_marital_normal.add_line()
        self.keyboard_marital_normal.add_button('в активном поиске', color=VkKeyboardColor.SECONDARY)
        self.keyboard_marital_normal.add_button('в гражданском браке', color=VkKeyboardColor.SECONDARY)

        self.keyboard_wrong = VkKeyboard(one_time=True)
        self.keyboard_wrong.add_button('Закончить', color=VkKeyboardColor.NEGATIVE)

        self.keyboard_new.get_keyboard()

    def send_photo(self, user_id: int, photo: dict):
        """
        Отправка фото в чат с пользователем
        :param user_id: Идентификатор пользователя
        :param photo: Ссылка на фотографию
        """
        self.vk_session.get_api().messages.send(
            user_id=user_id,
            random_id=get_random_id(),
            attachment=f'photo{photo["owner_id"]}_{photo["id"]}'
        )

    def send_msg(self, message: str, user_id: int, keyboard=None):
        """
        Сокращенная функция для отправки сообщения в чат с пользователем
        :param message: Текст сообщения;
        :param user_id: Идентификатор пользователя;
        :param keyboard: Отображаемая клавиатура.
        """
        self.vk_session.get_api().messages.send(
            user_id=user_id,
            random_id=get_random_id(),
            keyboard=keyboard,
            message=message
        )

    def listen_dialog(self) -> list:
        """
        Прослушка беседы с пользователем.
        :return: Список из характеристик о беседе с пользователем
        """
        lslongpooll = VkLongPoll(self.vk_session)
        for event in lslongpooll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                user_info = self.vk_session.get_api().users.get(
                    user_ids=event.user_id,
                    fields='sex,city,'
                )
                print(f'{event.user_id}: {event.text}')
                response = [user_info, event]
                return response

    def not_understand_msg(self, user_id: int):
        """
        Сообщение пользователю в случае сбоя программы
        :param user_id:  Идентификатор пользователя.
        """
        self.send_msg(message=f'Прости, я тебя не понимаю, давай попробуем начать все сначала',
                      user_id=user_id,
                      keyboard=self.keyboard_new.get_keyboard()
                      )

    def wrong_input(self, user_id: int):
        """
        Сообщение пользователю об ошибочном вводе
        :param user_id:  Идентификатор пользователя
        """
        self.send_msg(message=f'Кажется, что-то пошло не так\n'
                              f'Может попробуешь снова',
                      user_id=user_id,
                      )

    def check_city(self, city: str, user_id: int) -> bool:
        """
        Проверка на существование веденного города.(можно ввести не полностью город а первые буквы,
        при таком вводе, программа возьмет первый подходящий город)
        :param city:  Название города
        :param user_id:  Идентификатор пользователя
        :return: True - город существует, False - Город не существует.
        """
        city_result = self.service_session.get_api().database.getCities(
            country_id=1,
            q=city,
            need_all=0,
            count=1,
        )
        if city_result['count'] == 0:
            self.send_msg(message=f'Кажется такого города не существует.\nДавай попробуем снова. \n'
                                  f'Напиши существующий город...',
                          user_id=user_id,
                          keyboard=self.keyboard_settings.get_keyboard()
                          )
            return False
        return True

    def search_city_id(self, city: str) -> int:
        """
        Поиск ID города в базе ВК
        :param city:  Название города.
        :return: id города.
        """
        city_result = self.service_session.get_api().database.getCities(
            country_id=1,
            q=city,
            need_all=0,
            count=1,
        )
        print(city_result)
        return city_result['items'][0]['id']

    def cheng_sex(self, user_id: int) -> int:
        """
        Изменение параметра поиска: пол
        :param user_id:  Идентификатор пользователя.
        :return: id пола (2 - Мужской, 1 - Женский)
        """
        self.send_msg(message=f'На клавиатуре ниже выбери пол своей будущей второй половинки',
                      user_id=user_id,
                      keyboard=self.keyboard_sex.get_keyboard()
                      )
        while True:
            text = self.listen_dialog()[1].text
            if text == 'Мужской':
                return 2
            elif text == 'Женский':
                return 1
            else:
                self.send_msg(message=f'Кажется я тебя не понимаю'
                                      f'На клавиатуре ниже выбери пол своей будущей второй половинки',
                              user_id=user_id,
                              keyboard=self.keyboard_sex.get_keyboard()
                              )

    def cheng_city(self, user_id: int) -> str:
        """
        Изменение параметра поиска: Город
        :param user_id:  Идентификатор пользователя.
        :return: Название города
        """
        self.send_msg(message=f'Конечно мы можем поменять город.\n'
                              f'Какой город ты выберешь?',
                      user_id=user_id,
                      )
        return self.listen_dialog()[1].text

    def cheng_age(self, user_id: int) -> list:
        """
        Изменение параметра поиска: Возраст
        :param user_id:  Идентификатор пользователя.
        :return: Возрастной интервал в качестве списка
        """
        self.send_msg(message=f'На какой возраст ты бы хотел изменить? \n'
                              f'Напиши через пробел возрастной интервал.',
                      user_id=user_id,
                      )
        while True:
            text = self.listen_dialog()[1].text
            if text == 'Закончить':
                self.send_msg(message=f'Ииии... Закончили!',
                              user_id=user_id,
                              keyboard=self.keyboard_settings.get_keyboard()
                              )
                return None
            age = text.split()
            try:
                if int(age[0]) and int(age[1]):
                    return sorted(age, key=lambda x: int(x))
            except ValueError:
                self.wrong_input(user_id)

    def cheng_status(self, user_id: int) -> int:
        """
        Изменение параметра поиска: Семейное положение
        :param user_id:  Идентификатор пользователя.
        :return: id семейного положения
        """
        marital_status_dict = {
            'не женат (не замужем)': 1,
            'встречается': 2,
            'помолвлен(-а)': 3,
            'женат (замужем)': 4,
            'всё сложно': 5,
            'в активном поиске': 6,
            'влюблен(-а)': 7,
            'в гражданском браке': 8
        }
        self.send_msg(message=f'Хорошо и на что меняем',
                      user_id=user_id,
                      keyboard=self.keyboard_marital_normal.get_keyboard()
                      )
        text = self.listen_dialog()[1].text
        return marital_status_dict[text]

    def shove_favorite(self, db_list: object, user_id: int):
        """
        Сообщение демонстрирующее список избранных пользователей
        :param db_list: список избранных из БД;
        :param user_id:  Идентификатор пользователя.
        """
        if db_list:
            self.send_msg(message=f'Список избранных:\n',
                          user_id=user_id,
                          )
            for find_person in db_list:
                self.send_msg(message=f'@id{find_person.search_user_id}({find_person.search_user_name})\n',
                              user_id=user_id,
                              )
        else:
            self.send_msg(message=f'Похоже, ты еще некого не добавил в избранное',
                          user_id=user_id,
                          keyboard=self.keyboard_old.get_keyboard()
                          )

    def i_not_understand(self, user_id: int):
        """
        Сообщение пользователю выводиться на неопознанные команды боту
        :param user_id:  Идентификатор пользователя.
        """
        else_msg = [
            'Не понимаю о чем ты!',
            'Что-то на непонятном\n давай попробуем еще раз',
            'Кажется, я не знаю таких команд\n я же всего лишь бот',
            'Воу-воу, полегче. Я всего лишь структурированный код(хотелось бы в это верить)\n',
            'Так, давай вот без этого.',
            'А можно не отклоняться от сценария?\n\n Спасибо...',
            'B и что мне с эти делать?'
        ]
        self.send_msg(message=random.choice(else_msg),
                      user_id=user_id,
                      keyboard=self.keyboard_old.get_keyboard())

    def msg_setting_remember(self, user_id: int):
        """
        Сообщение о том что были произведены изменения
        :param user_id:  Идентификатор пользователя.
        """
        self.send_msg(message=f'Хорошо. что-то еще?',
                      user_id=user_id,
                      keyboard=self.keyboard_settings.get_keyboard()
                      )

    def msg_settings_save(self, user_id: int):
        """
       Сообщение о том что была произведена запись в БД
       :param user_id:  Идентификатор пользователя.
       """
        self.send_msg(message=f'Я всё запомнил!\n'
                              f'Ну что приступим к поиску.',
                      user_id=user_id,
                      keyboard=self.keyboard_old.get_keyboard()
                      )

    # def keyboard_find(self, user_id: int):
    #     self.send_msg(message='',
    #                   user_id=user_id,
    #                   keyboard=self.keyboard_old_find.get_keyboard()
    #                   )

    def new_user_search(self, user_id: int) -> dict:
        """
        Настройка запроса нового пользователя
        :param user_id:  Идентификатор пользователя.
        :return: Словарь из настроенных характеристик
        """
        marital_status = int
        next_msg = True
        sex = int
        marital_status_dict = {
            'не женат (не замужем)': 1,
            'встречается': 2,
            'помолвлен(-а)': 3,
            'женат (замужем)': 4,
            'всё сложно': 5,
            'в активном поиске': 6,
            'влюблен(-а)': 7,
            'в гражданском браке': 8
        }

        self.send_msg(message=f'Для начала на клавиатуре ниже выбери пол своей будущей второй половинки',
                      user_id=user_id,
                      keyboard=self.keyboard_sex.get_keyboard()
                      )
        text = self.listen_dialog()[1].text
        if text == 'Мужской':
            sex = 2
        elif text == 'Женский':
            sex = 1
        else:
            self.not_understand_msg(user_id)

        self.send_msg(message=f'Отлично! Продолжаем. \n'
                              f'Напиши через пробел возрастной интервал.',
                      user_id=user_id,
                      )
        while True:
            text = self.listen_dialog()[1].text
            if text == 'Закончить':
                self.send_msg(message=f'Ииии... Закончили!',
                              user_id=user_id,
                              keyboard=self.keyboard_sex.get_keyboard()
                              )

                return None
            age = text.split()
            try:
                age = sorted(age, key=lambda x: int(x))
                if int(age[0]) and int(age[1]):
                    break
            except ValueError:
                self.wrong_input(user_id)

        self.send_msg(message=f'Пришло время выбрать город.\n'
                              f'Какой город ты выберешь?',
                      user_id=user_id,
                      )
        while True:
            city = self.listen_dialog()[1].text
            if self.check_city(city, user_id):
                break
            else:
                self.send_msg(message=f'Вроде бы такого города не существует\n'
                                      f'Введи заново',
                              user_id=user_id,
                              )
        self.send_msg(message=f'Остался последний пункт надеюсь ты к нему готов.\n'
                              f'Выбери семейное положение.\n'
                              f'Хорошенько подумай прежде чем решить, тут ты не можешь ошибиться.\n'
                              f'Выберешь однажды - не сможешь изменить никогда!!!👻',
                      user_id=user_id,
                      )
        self.send_msg(message=f'Шучу, ты всегда сможешь изменить настройки поиска😜',
                      user_id=user_id,
                      keyboard=self.keyboard_marital_normal.get_keyboard()
                      )
        text = self.listen_dialog()[1].text

        search_dict = {
            'sex': sex,
            'age_from': age[0],
            'age_to': age[1],
            'city': city,
            'marital_status': marital_status_dict[text]
        }
        return search_dict
