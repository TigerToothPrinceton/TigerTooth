import psycopg2
from sys import argv, stderr
from os import path
from datetime import datetime


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

    def add_reaction(self, data):
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

    def add_food(self, new_foods, dhall):
        try:
            cursor = self._connection.cursor()
            for new_food in new_foods:
                # is the new food already in the food table
                boolean_query = "SELECT EXISTS(SELECT 1 FROM food WHERE api_id='{}' and dhall='{}')".format(
                    new_food['id'], dhall)
                cursor.execute(boolean_query)
                if cursor.fetchone()[0] == False:
                    insert_query = "INSERT INTO food (name, num_ratings, num_stars, dhall, last_served, api_id) VALUES (%s, %s, %s, %s, %s, %s)"
                    insert_arr = [new_food['name'], 0, 0, dhall, datetime.today().strftime(
                        '%Y-%m-%d'), new_food['id']]
                    cursor.execute(insert_query, insert_arr)
                    self._connection.commit()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception(
                'Failed to insert new food into PostgreSQL table')

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

    def add_food_image(self, food_id, food_url):
        try:
            cursor = self._connection.cursor()
            update_query = "UPDATE food SET url = '{}' WHERE food.food_id = '{}'".format(
                food_url, food_id)
            cursor.execute(update_query)
            self._connection.commit()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception(
                'Failed to insert food image into PostgreSQL table')
