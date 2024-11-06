import sqlite3


def initiate_db():
    with sqlite3.connect('basa_14_4.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Products (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                price INTEGER NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                age INTEGER NOT NULL,
                balance INTEGER NOT NULL
            )
        ''')
        conn.commit()


def add_products():
    products = [
        ('Бургер', 'Для набора веса №1', 300),
        ('Торт', 'Для набора веса №2', 500),
        ('Конфеты', 'Для набора веса №3', 200),
        ('Пурген', 'Для худеющих', 700),
    ]
    with sqlite3.connect('basa_14_4.db') as conn:
        cursor = conn.cursor()
        for product in products:
            cursor.execute('SELECT COUNT(*) FROM Products WHERE title = ?', (product[0],))
            if cursor.fetchone()[0] == 0:
                cursor.execute('INSERT INTO Products (title, description, price) VALUES (?, ?, ?)', product)
        conn.commit()


def get_all_products():
    with sqlite3.connect('basa_14_4.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Products')
        return cursor.fetchall()


def add_user(username, email, age):
    balance = 1000
    with sqlite3.connect('basa_14_4.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Users (username, email, age, balance) VALUES (?, ?, ?, ?)',
                       (username, email, age, balance))
        conn.commit()


def is_included(username):
    with sqlite3.connect('basa_14_4.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM Users WHERE username = ?', (username,))
        return cursor.fetchone()[0] > 0


initiate_db()
add_products()
products = get_all_products()
