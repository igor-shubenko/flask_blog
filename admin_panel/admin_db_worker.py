import sqlite3

class AdminDBWorker():
    """Класс для работы с базой данных"""

    def __init__(self, db):
        self.__db = db
        self.__cursor = self.__db.cursor()

    def check_admin_exist(self):
        query = 'SELECT * FROM admins'
        try:
            self.__cursor.execute(query)
            result = self.__cursor.fetchall()
            return len(result) > 0
        except sqlite3.Error as e:
            print(e)

    def add_admin(self, admin_name, pass_hash):
        query = 'INSERT INTO admins(name, pass_hash) VALUES(?, ?)'
        values = (admin_name, pass_hash)
        try:
            self.__cursor.execute(query, values)
            self.__db.commit()
        except sqlite3.Error as e:
            print(e)
            return False
        return True

    def get_admin_name(self):
        query = 'SELECT name FROM admins'
        try:
            self.__cursor.execute(query)
            result = self.__cursor.fetchall()
            return result[0]['name']
        except sqlite3.Error as e:
            print(e)
            return False

    def get_admin_psw_hash(self):
        query = 'SELECT pass_hash FROM admins'
        try:
            self.__cursor.execute(query)
            result = self.__cursor.fetchall()
            return result[0]['pass_hash']
        except sqlite3.Error as e:
            print(e)
            return False

    def add_post(self, title, slug, text):
        query = 'INSERT INTO posts(title, post_slug, post_text) VALUES(?, ?, ?)'
        value = (title, slug, text)
        try:
            self.__cursor.execute(query, value)
            self.__db.commit()
        except sqlite3.Error as e:
            print(e)
            return False
        return True

    def check_post_slug(self, slug):
        query = f"SELECT COUNT() AS count FROM posts WHERE post_slug=?"
        try:
            self.__cursor.execute(query, (slug,))
            result = self.__cursor.fetchall()  # result это список со словарями
            if result[0]['count'] == 0:
                return True
            return False
        except sqlite3.Error as e:
            print(e)


    def get_post(self, post_slug):
        """Returns post data"""
        query = f"Select * FROM posts WHERE post_slug=?"
        try:
            self.__cursor.execute(query, (post_slug,))
            result = self.__cursor.fetchall()
            return result
        except sqlite3.Error as e:
            print(e)
            return False

    def edit_post(self, title, slug, text):
        query = f'UPDATE posts SET title=?, post_text=? WHERE post_slug=?'
        values = (title, text, slug)
        print(values)
        try:
            self.__cursor.execute(query, values)
            self.__db.commit()
        except sqlite3.Error as e:
            print(e)
            return False
        return True