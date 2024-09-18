import mysql.connector
from mysql.connector import Error

class NewsService:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def _connect(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return connection
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            return None

    def get_candidate_news(self):
        connection = self._connect()
        
        if connection is None:
            return None

        try:
            cursor = connection.cursor()
            query = """
                SELECT id, title
                FROM news
                WHERE publish_date >= (SELECT MAX(publish_date) FROM news) - INTERVAL 1 DAY;
            """
            cursor.execute(query)
            return cursor.fetchall()

        except Error as e:
            print(f"Error while retrieving candidate news: {e}")
            return None

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def get_clicked_news(self, user_id):
        connection = self._connect()
        
        if connection is None:
            return None

        try:
            cursor = connection.cursor()
            query = """
                SELECT nc.news_id, n.title
                FROM news_click_log nc
                INNER JOIN news n ON nc.news_id = n.id
                WHERE nc.user_id = %s
                ORDER BY nc.created_date DESC
                LIMIT 50;
            """
            cursor.execute(query, (user_id,))
            return cursor.fetchall()

        except Error as e:
            print(f"Error while retrieving clicked news: {e}")
            return None

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()