import psycopg2
from sys import argv, stderr
from os import path


class Database():

    def __init__(self):
        self._connection = None

    def connect(self):
        try:
            self._connection = psycopg2.connect(host="ec2-54-159-175-113.compute-1.amazonaws.com",
                                                database="d27qk32tcn1bc",
                                                user="btpesghzoocreg",
                                                password="c35d066fbff924a2c15d6b2bbb9969078fd4c1cd60f1737dbdef7e717ee903f1")
        except Exception as e:
            print(f'{e}', file=stderr)

    def disconnect(self):
        self._connection.close()

    def reaction_submit(self, data):
        try:
            cursor = self._connection.cursor()

            postgres_insert_query = """INSERT INTO reactions (reaction, userID, dhall, time) VALUES (%s, %d, %s, %s)"""

            cursor.execute(postgres_insert_query, data)
            self._connection.commit()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception(
                'Failed to insert record into PostgreSQL table')

    def get_reactions(self, dhall):
        try:
            cursor = self._connection.cursor()
            get_query = "SELECT * FROM reactions WHERE reactions.dhall=?"
            cursor.execute(get_query, [dhall])
            return cursor.fetchall()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception('Failed to get rows PostgreSQL table')

    def get_names(self, dhall):
        try:
            cursor = self._connection.cursor()
            get_query = "SELECT food.name food.numStars FROM food WHERE food.dhall=?"
            cursor.execute(get_query, [dhall])
            ## name, ingredients, numRatings, numStars, description, url, dhall, lastServed
            return cursor.fetchall()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception('Failed to get rows PostgreSQL table')

    def get_food(self, name):
        try:
            cursor = self._connection.cursor()
            ## name, ingredients, numRatings, numStars, description, url, dhall, lastServed
            sql_command = "SELECT food.description food.numStars FROM food WHERE food.name=?"
            cursor.execute(sql_command, [name])
            return cursor.fetchall()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception('Failed to get rows PostgreSQL table')
                
