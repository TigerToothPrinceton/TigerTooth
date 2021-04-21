import psycopg2
from sys import argv, stderr
from os import path
from datetime import datetime
import pytz


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

            insert_query = "INSERT INTO reactions (reaction, net_id, dhall, time) VALUES (%s, %s, %s, %s)"

            cursor.execute(insert_query, data)
            self._connection.commit()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception(
                'Failed to insert reaction into PostgreSQL table')

    def get_reactions(self, dhall):
        try:
            cursor = self._connection.cursor()
            get_query = "SELECT * FROM reactions WHERE reactions.dhall='{}' ORDER BY reactions.reactions_id DESC".format(
                dhall)
            cursor.execute(get_query)
            return cursor.fetchall()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception('Failed to get reactions from PostgreSQL table')

    def add_food(self, new_foods, dhall):
        try:
            cursor = self._connection.cursor()
            est = pytz.timezone('US/Eastern')
            for new_food in new_foods:
                # is the new food already in the food table
                boolean_query = "SELECT EXISTS(SELECT 1 FROM food WHERE api_id='{}' and dhall='{}')".format(
                    new_food['id'], dhall)
                cursor.execute(boolean_query)
                if cursor.fetchone()[0] == False:
                    insert_query = "INSERT INTO food (name, num_ratings, num_stars, dhall, last_served, api_id) VALUES (%s, %s, %s, %s, %s, %s)"
                    insert_arr = [new_food['name'], 0, 0, dhall, datetime.today().astimezone(est).strftime(
                        '%Y-%m-%d'), new_food['id']]
                    cursor.execute(insert_query, insert_arr)
                    self._connection.commit()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception(
                'Failed to insert new food into PostgreSQL table')

    def get_food(self, api_id, dhall):
        try:
            cursor = self._connection.cursor()
            get_query = "SELECT food.url, food.name, food.num_ratings, food.num_stars, food.food_id, food.api_id FROM food WHERE food.api_id='{}' and food.dhall='{}'".format(
                api_id, dhall)
            cursor.execute(get_query)
            return cursor.fetchone()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception(
                'Failed to get an individual food item from PostgreSQL table')

    def get_foods(self, dhall):
        try:
            cursor = self._connection.cursor()
            get_query = "SELECT food.url, food.name, food.num_ratings, food.num_stars, food.food_id, food.api_id FROM food WHERE food.dhall='{}'".format(
                dhall)
            cursor.execute(get_query)
            return cursor.fetchall()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception('Failed to get foods from PostgreSQL table')

    def get_food_info(self, food_id):
        try:
            cursor = self._connection.cursor()
            get_query = "SELECT food.url, food.name, food.num_ratings, food.num_stars FROM food WHERE food.food_id='{}'".format(
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
            get_query = "SELECT reviews.review FROM reviews WHERE reviews.food_id='{}' ORDER BY reviews.time DESC, reviews.review_id DESC".format(
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
            boolean_query = "SELECT EXISTS(SELECT 1 FROM reviews WHERE net_id='{}' and food_id='{}')".format(
                review_data[0], review_data[1])
            cursor.execute(boolean_query)
            # user never reviews this food
            if cursor.fetchone()[0] == False:
                insert_query = "INSERT INTO reviews (net_id, food_id, review, rating, time) VALUES (%s, %s, %s, %s, %s)"
                update_query = "UPDATE food SET num_ratings = num_ratings + 1, num_stars = num_stars + '{}' WHERE food.food_id = '{}'".format(
                    rating, food_id)
                cursor.execute(insert_query, review_data)
                cursor.execute(update_query)
                self._connection.commit()

                get_query = "SELECT review_id FROM reviews WHERE net_id='{}' and food_id='{}'".format(
                    review_data[0], review_data[1])
                cursor.execute(get_query)
                review_id = cursor.fetchone()[0]
                update_query = "UPDATE users SET rev_rate = array_append(rev_rate, '{}') WHERE net_id = '{}'".format(
                    review_id, review_data[0])
                cursor.execute(update_query)
                self._connection.commit()
            else:
                get_query = "SELECT rating FROM reviews WHERE net_id='{}' and food_id='{}'".format(
                    review_data[0], review_data[1])
                cursor.execute(get_query)
                old_rating = cursor.fetchone()[0]
                update_query = "UPDATE reviews SET review = '{}', rating = '{}', time = '{}' WHERE reviews.net_id = '{}' AND reviews.food_id = '{}'".format(
                    review_data[2], rating, review_data[4], review_data[0], review_data[1])
                cursor.execute(update_query)
                update_query = "UPDATE food SET num_stars = num_stars - '{}' + '{}' WHERE food.food_id = '{}'".format(
                    old_rating, rating, food_id)
                cursor.execute(update_query)
                self._connection.commit()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception(
                'Failed to insert/update review in PostgreSQL table')

    def add_food_image(self, api_id, food_url):
        try:
            cursor = self._connection.cursor()
            update_query = "UPDATE food SET url = '{}' WHERE food.api_id = '{}'".format(
                food_url, api_id)
            cursor.execute(update_query)
            self._connection.commit()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception(
                'Failed to insert food image into PostgreSQL table')

    def clear_db(self, meal):
        try:
            cursor = self._connection.cursor()
            time1 = 20
            time2 = 5
            if meal == "Breakfast":
                time1 = 5
                time2 = 10
            if meal == "Lunch":
                time1 = 10
                time2 = 14
            if meal == "Dinner":
                time1 = 14
                time2 = 20
            delete_query = "DELETE from reactions WHERE ".format(
                food_url, api_id)
            cursor.execute(update_query)
            self._connection.commit()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception(
                'Failed to remove reactions')

    def add_user(self, netid):
        try:
            cursor = self._connection.cursor()
            # is this user already in the users table
            boolean_query = "SELECT EXISTS(SELECT 1 FROM users WHERE net_id='{}')".format(
                netid)
            cursor.execute(boolean_query)
            if cursor.fetchone()[0] == False:
                insert_query = "INSERT INTO users (net_id) VALUES (%s)"
                cursor.execute(insert_query, [netid])
                self._connection.commit()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception(
                'Failed to add user into PostgreSQL table')

    def get_history(self, net_id):
        try:
            cursor = self._connection.cursor()
            ## name, ingredients, numRatings, numStars, description, url, dhall, lastServed
            # get_query = "SELECT rev_rate FROM users WHERE net_id = '{}'".format(
            #     net_id)
            # cursor.execute(get_query)
            # reviews_arr = cursor.fetchone()[0]
            # for review_id in reviews_arr:
            get_query = "SELECT food_id, review, rating FROM reviews WHERE net_id = '{}'".format(
                net_id)
            cursor.execute(get_query)
            reviews_arr = cursor.fetchall()
            result_arr = []
            for reviews in reviews_arr:
                food_id = reviews[0]
                review = reviews[1]
                rating = reviews[2]
                get_query = "SELECT name, url, dhall, api_id FROM food WHERE food_id = '{}'".format(
                    food_id)
                cursor.execute(get_query)
                result = list(cursor.fetchone())
                result.append(rating)
                result.append(review)
                result_arr.append(result)
            return result_arr

        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception(
                'Failed to get food item review from PostgreSQL table')
