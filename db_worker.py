import sqlite3


class DBWorker:
    """Класс для работы с базой данных"""
    def __init__(self, db):
        self.__db = db
        self.__cursor = self.__db.cursor()


    def get_all_posts(self):
        query = "SELECT * FROM posts WHERE post_slug NOT IN('index', 'about') ORDER BY post_date DESC"
        try:
            self.__cursor.execute(query)
            result = self.__cursor.fetchall()    # result это список со словарями
            if result:
                return result
        except sqlite3.Error as e:
            print(e)
        return []

    def record_feedback(self, name, email, message):
        """Writes to DB feedback text"""
        query = 'INSERT INTO feedbacks (name, email, message) VALUES(?, ?, ?)'
        values = (name, email, message)
        try:
            self.__cursor.execute(query, values)
            self.__db.commit()
        except sqlite3.Error as e:
            print(e)
            return False
        return True

    def check_username(self, username):
        """Check if username is already in DB"""
        query = f"SELECT COUNT() AS count FROM users WHERE name=?"
        try:
            self.__cursor.execute(query, (username,))
            result = self.__cursor.fetchall()    # result это список со словарями
            if result[0]['count'] != 0:
                return True
            return False
        except sqlite3.Error as e:
                print(e)

    def check_email(self, email):
        """Checks if email is already registered by user in DB"""
        print(email)
        query = f"SELECT COUNT() AS count FROM users WHERE email=?"
        try:
            self.__cursor.execute(query, (email,))
            result = self.__cursor.fetchall()   # result это список со словарями
            if result[0]['count'] != 0:
                return True
            return False
        except sqlite3.Error as e:
                print(e)


    def register_user(self, username, user_email, password_hash):
        """Добавляет новую учетную записть пользователя"""
        query = 'INSERT INTO users (name, email, pass_hash) VALUES(?,?,?)'
        values = (username, user_email, password_hash)
        try:
            self.__cursor.execute(query, values)
            self.__db.commit()
        except sqlite3.Error as e:
            print(e)
            return False
        return True

    def get_pswhash(self, username):
        """Returns users password hash"""
        query = f"SELECT pass_hash FROM users WHERE name=?"
        try:
            self.__cursor.execute(query, (username,))
            result = self.__cursor.fetchall()
            return result[0]['pass_hash']
        except sqlite3.Error as e:
            print(e)
            return False

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

    def add_comment(self, post_id, name, text):
        query = 'INSERT INTO comments (name, text, post_id) VALUES(?,?,?)'
        values = (name, text, post_id)
        try:
            self.__cursor.execute(query, values)
            self.__db.commit()
        except sqlite3.Error as e:
            print(e)
            return False
        return True

    def get_post_comments(self, post_id):
        query = f'SELECT *, CAST(JULIANDAY("NOW")-JULIANDAY(date_add) AS INT) as days_ago FROM comments WHERE post_id=? ORDER BY date_add DESC'
        try:
            self.__cursor.execute(query, (post_id,))
            result = self.__cursor.fetchall()
            return result
        except sqlite3.Error as e:
            print(e)
            return False


