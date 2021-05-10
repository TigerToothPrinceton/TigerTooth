import psycopg2
from sys import argv, stderr
# from os import path
import os
from datetime import datetime
import pytz
from selenium import webdriver
import image_scrape

CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'
chrome_bin = os.environ.get('GOOGLE_CHROME_BIN', 'chromedriver')
options = webdriver.ChromeOptions()
options.binary_location = chrome_bin
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--headless')


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

            insert_query = "INSERT INTO reactions (reaction, net_id, dhall, time, hour) VALUES (%s, %s, %s, %s, %s)"

            cursor.execute(insert_query, data)
            self._connection.commit()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception(
                'Failed to insert reaction into PostgreSQL table')

    def get_reactions(self, dhall):
        try:
            cursor = self._connection.cursor()
            get_query = "SELECT * FROM reactions WHERE reactions.dhall=%s ORDER BY reactions.reactions_id ASC"
            cursor.execute(get_query, [dhall])
            return cursor.fetchall()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception('Failed to get reactions from PostgreSQL table')

    def get_new_reactions(self, reaction_id, dhall):
        try:
            cursor = self._connection.cursor()
            get_query = "SELECT * FROM reactions WHERE reactions.dhall=%s AND reactions.reactions_id>%s ORDER BY reactions.reactions_id ASC"
            cursor.execute(get_query, [dhall, reaction_id])
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
                boolean_query = "SELECT EXISTS(SELECT 1 FROM food WHERE api_id=%s and dhall=%s)"
                cursor.execute(boolean_query, [new_food['id'], dhall])
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
            get_query = "SELECT food.url, food.name, food.num_ratings, food.num_stars, food.food_id, food.api_id FROM food WHERE food.api_id=%s and food.dhall=%s"
            cursor.execute(get_query, [api_id, dhall])
            return cursor.fetchone()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception(
                'Failed to get an individual food item from PostgreSQL table')

    def get_foods(self, dhall):
        try:
            cursor = self._connection.cursor()
            get_query = "SELECT food.url, food.name, food.num_ratings, food.num_stars, food.food_id, food.api_id FROM food WHERE food.dhall=%s"
            cursor.execute(get_query, [dhall])
            return cursor.fetchall()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception('Failed to get foods from PostgreSQL table')

    def get_food_info(self, food_id):
        try:
            cursor = self._connection.cursor()
            get_query = "SELECT food.url, food.name, food.num_ratings, food.num_stars FROM food WHERE food.food_id=%s"
            cursor.execute(get_query, [food_id])
            return cursor.fetchall()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception(
                'Failed to get individual food item from PostgreSQL table')

    def get_reviews(self, food_id):
        try:
            cursor = self._connection.cursor()
            ## name, ingredients, numRatings, numStars, description, url, dhall, lastServed
            get_query = "SELECT reviews.review FROM reviews WHERE reviews.food_id=%s ORDER BY reviews.time DESC, reviews.review_id DESC"
            cursor.execute(get_query, [food_id])
            return cursor.fetchall()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception(
                'Failed to get food item review from PostgreSQL table')

    def add_review(self, review_data, rating, food_id):
        try:
            cursor = self._connection.cursor()
            boolean_query = "SELECT EXISTS(SELECT 1 FROM reviews WHERE net_id=%s and food_id=%s)"
            cursor.execute(boolean_query, [review_data[0], review_data[1]])
            # user never reviews this food
            if cursor.fetchone()[0] == False:
                insert_query = "INSERT INTO reviews (net_id, food_id, review, rating, time, date) VALUES (%s, %s, %s, %s, %s, %s)"
                update_query = "UPDATE food SET num_ratings = num_ratings + 1, num_stars = num_stars + %s WHERE food.food_id = %s"
                cursor.execute(insert_query, review_data)
                cursor.execute(update_query, [rating, food_id])
                self._connection.commit()

                get_query = "SELECT review_id FROM reviews WHERE net_id=%s and food_id=%s"
                cursor.execute(get_query, [review_data[0], review_data[1]])
                review_id = cursor.fetchone()[0]
                update_query = "UPDATE users SET rev_rate = array_append(rev_rate, %s) WHERE net_id = %s"
                cursor.execute(update_query, [review_id, review_data[0]])
                self._connection.commit()
            else:
                get_query = "SELECT rating FROM reviews WHERE net_id=%s and food_id=%s"
                cursor.execute(get_query, [review_data[0], review_data[1]])
                old_rating = cursor.fetchone()[0]
                update_query = "UPDATE reviews SET review = %s, rating = %s, time = %s, date = %s WHERE reviews.net_id = %s AND reviews.food_id = %s"
                cursor.execute(update_query, [
                               review_data[2], rating, review_data[4], review_data[5], review_data[0], review_data[1]])
                update_query = "UPDATE food SET num_stars = num_stars - %s + %s WHERE food.food_id = %s"
                cursor.execute(update_query, [old_rating, rating, food_id])
                self._connection.commit()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception(
                'Failed to insert/update review in PostgreSQL table')

    def add_food_images(self, api_ids, dhall):
        try:
            cursor = self._connection.cursor()
            for api_id in api_ids:
                food = self.get_food(int(api_id), dhall)
                food_url = food[0]
                food_name = food[1]
                if food_url == None or food_url == "":
                    # Scrape an image for this new food from Google unless an error occurs
                    try:
                        with webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=options) as wd:
                            food_img_url = image_scrape.fetch_image_urls(
                                food_name, 1, wd=wd, sleep_between_interactions=0.5)
                    except Exception:
                        pass
                    update_query = "UPDATE food SET url = %s WHERE food.api_id = %s AND food.dhall = %s"
                    cursor.execute(
                        update_query, [food_img_url.pop(), api_id, dhall])
                    self._connection.commit()
            return "Finished inserting images"
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception(
                'Failed to insert food images into PostgreSQL table')

    def clear_db(self, meal):
        try:
            cursor = self._connection.cursor()
            time1 = 20
            time2 = 5

            if meal == "Breakfast":
                time1 = 5
                time2 = 10
                delete_query = "DELETE from reactions WHERE reactions.hour < %s OR reactions.hour >= %s"
                cursor.execute(delete_query, [time1, time2])
                self._connection.commit()
            if meal == "Lunch":
                time1 = 10
                time2 = 16
                delete_query = "DELETE from reactions WHERE reactions.hour < %s OR reactions.hour >= %s"
                cursor.execute(delete_query, [time1, time2])
                self._connection.commit()
            if meal == "Dinner":
                time1 = 16
                time2 = 24
                delete_query = "DELETE from reactions WHERE reactions.hour < %s OR reactions.hour >= %s"
                cursor.execute(delete_query, [time1, time2])
                self._connection.commit()

        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception(
                'Failed to remove reactions')

    def add_user(self, netid):
        try:
            cursor = self._connection.cursor()
            # is this user already in the users table
            boolean_query = "SELECT EXISTS(SELECT 1 FROM users WHERE net_id=%s)"
            cursor.execute(boolean_query, [netid])
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
            get_query = "SELECT food_id, review, rating FROM reviews WHERE net_id = %s"
            cursor.execute(get_query, [net_id])
            reviews_arr = cursor.fetchall()
            result_arr = []
            for reviews in reviews_arr:
                food_id = reviews[0]
                review = reviews[1]
                rating = reviews[2]
                get_query = "SELECT name, url, dhall, api_id FROM food WHERE food_id = %s"
                cursor.execute(get_query, [food_id])
                result = list(cursor.fetchone())
                result.append(rating)
                result.append(review)
                result.append(food_id)
                result_arr.append(result)
            return result_arr

        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception(
                'Failed to get food item review from PostgreSQL table')

    def delete_photo(self, food_id, dhall):
        try:
            cursor = self._connection.cursor()
            update_query = "UPDATE food SET url = %s WHERE food.food_id = %s AND food.dhall= %s"
            cursor.execute(update_query, [None, food_id, dhall])
            self._connection.commit()
            return "Successfully removed food image from PostgreSQL table"
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception(
                'Failed to remove food image from PostgreSQL table')
