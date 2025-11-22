import mysql.connector
from mysql.connector import Error

class DatabaseConfig:
    @staticmethod
    def get_connection():
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='college_erp2',  # Changed to match your database
                user='root',
                password='6604',  # Your MySQL password
                auth_plugin='mysql_native_password'
            )
            return connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None