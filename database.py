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

            insert_query = "INSERT INTO reactions (reaction, user_id, dhall, time) VALUES (%s, %s, %s, %s)"

            cursor.execute(insert_query, data)
            self._connection.commit()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception(
                'Failed to insert reaction into PostgreSQL table')

    def get_reactions(self, dhall):
        try:
            cursor = self._connection.cursor()
            get_query = "SELECT * FROM reactions WHERE reactions.dhall='{}'".format(
                dhall)
            cursor.execute(get_query)
            return cursor.fetchall()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception('Failed to get reactions from PostgreSQL table')

    def get_foods(self, dhall):
        try:
            cursor = self._connection.cursor()
            get_query = "SELECT food.url, food.name, food.num_ratings, food.num_stars, food.food_id FROM food WHERE food.dhall='{}'".format(
                dhall)
            cursor.execute(get_query)
            return cursor.fetchall()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception('Failed to get foods from PostgreSQL table')

    def get_food_info(self, food_id):
        try:
            cursor = self._connection.cursor()
            get_query = "SELECT food.url, food.name, food.num_ratings, food.num_stars, food.description FROM food WHERE food.food_id='{}'".format(
                food_id)
            cursor.execute(get_query)
            return cursor.fetchall()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception(
                'Failed to get individual food item from PostgreSQL table')

    def get_reviews(self, food_id):
        try:
            cursor = self._connection.cursor()
            ## name, ingredients, numRatings, numStars, description, url, dhall, lastServed
            get_query = "SELECT reviews.review FROM reviews WHERE reviews.food_id='{}' ORDER BY reviews.time ASC".format(
                food_id)
            cursor.execute(get_query)
            return cursor.fetchall()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception(
                'Failed to get food item review from PostgreSQL table')

    def add_review(self, review_data, rating, food_id):
        try:
            cursor = self._connection.cursor()
            insert_query = "INSERT INTO reviews (user_id, food_id, review, rating, time) VALUES (%s, %s, %s, %s, %s)"
            update_query = "UPDATE food SET num_ratings = num_ratings + 1, num_stars = num_stars + '{}' WHERE food.food_id = '{}'".format(
                rating, food_id)
            cursor.execute(insert_query, review_data)
            cursor.execute(update_query)
            self._connection.commit()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception(
                'Failed to insert review into PostgreSQL table')
