import sqlite3 # Импортирование библиотеки для работы с БД
from aiogram import Router

database_R = Router()

def create_table():
    conn = sqlite3.connect("users.sql") # Создание БД
    cursor = conn.cursor() # Через курсор будет происходить выполнение комманд для БД
    cursor.execute('CREATE TABLE IF NOT EXISTS users(id int auto_increment primary key, telegram_id varchar(30), name varchar(30), username varchar(50))') # Подготовка комманды к выполнению
    conn.commit() # выполнение комманды
    cursor.close() # Закрытие курсора
    conn.close() # Разрыв соединения

def register(message):
    user_id = str(message.from_user.id)
    first_name = message.from_user.first_name
    username = message.from_user.username

    conn = sqlite3.connect("users.sql")  # Подключение к БД
    cursor = conn.cursor()  # Через курсор будет происходить выполнение комманд для БД
    cursor.execute('SELECT telegram_id FROM users') # Запрос БД на получение id всех зарегистрированных пользователей
    users_id_data = cursor.fetchall() # Получение id всех зарегистрированных пользователей
    # Проверка на присутствие пользователя в БД
    user_exists = False
    for i in users_id_data:
        if (i[0] == user_id) and (not user_exists):
            user_exists = True
            break

    if not user_exists:
        print(f"Выполнение регистрации пользователя: {user_id}; {first_name}; {username}")
        cursor.execute('INSERT INTO users (telegram_id, name, username) VALUES("%s","%s","%s")' % (user_id, first_name, username))  # Подготовка комманды к выполнению
        conn.commit()
        print("Регистрация прошла успешно")

    cursor.close()  # Закрытие курсора
    conn.close()  # Разрыв соединения

def get_users(message):
    conn = sqlite3.connect("users.sql")  # Подключение к БД
    cursor = conn.cursor()  # Через курсор будет происходить выполнение комманд для БД
    cursor.execute('SELECT * FROM users')
    users_data = cursor.fetchall() # Возвращение всех найденных записей, fetchall - используется когда надо получить данные
    info = ''
    for i in users_data:
        info += f"ID: {i[1]}; Имя: {i[2]}, Username: {i[3]}\n"

    database_R.message(message.chat.id, info)
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_table()

