# VK_inder
## Программа для поиска людей по определенным характеристикам.
Для работы программы необходимо:
- создать ВК группу
- создать ВК приложение
- создать базу данных (SQLPostgres)
### Входные данные VK в main.py:
```python3
TOKEN_VK_GROUP = Sicret_deta.TOKEN_VK_GROUP
SERVICE_KEY = Sicret_deta.SERVICE_KEY
USER_TOKEN = Sicret_deta.USER_TOKEN
```
- TOKEN_VK_GROUP  - [токен](https://vk.com/dev/access_token?f=2.%20%D0%9A%D0%BB%D1%8E%D1%87%20%D0%B4%D0%BE%D1%81%D1%82%D1%83%D0%BF%D0%B0%20%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D1%81%D1%82%D0%B2%D0%B0) группы вк
- SERVICE_KEY - [сервесный ключ](https://vk.com/dev/access_token?f=3.%20%D0%A1%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D0%BD%D1%8B%D0%B9%20%D0%BA%D0%BB%D1%8E%D1%87%20%D0%B4%D0%BE%D1%81%D1%82%D1%83%D0%BF%D0%B0) приложениея
- USER_TOKEN - [Токен пользователя](https://vk.com/dev/access_token?f=1.%20%D0%9A%D0%BB%D1%8E%D1%87%20%D0%B4%D0%BE%D1%81%D1%82%D1%83%D0%BF%D0%B0%20%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8F)


### Входные данные базы данных в main.py:
```python3
BD_USER = 'vk'
USER_PASSWORD = '12345678'
BD_NAME = 'vkinder_db'
```
- BD_USER - имя пользователя БД
- USER_PASSWORD - пароль пользователя БД
- BD_NAME - имя БД

После запуска **main.py** можно заходить в чат с группой и выполнять поиск.
#### P.S:
На данный момент бот запрашивает у пользователя токе, пользователя для поиска людей, весьма варварским методом. Возможно, в будущем это измениться.
