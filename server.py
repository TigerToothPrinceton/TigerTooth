from flask import Flask, request, make_response, redirect, url_for
from flask import render_template
from database import Database
from datetime import datetime
from CASClient import CASClient
from requests_lib import RequestsLib
import datetime
# import requests


### IMPORTANT: Dining Hall Menu only keeps 2 weeks of data ###

# please note: this is not a permanent access token... it needs to be refreshed a ton (1000 hrs)
# configs = {"BASE_URL": "https://api.princeton.edu:443/mobile-app/1.0.0/",
#    "ACCESS_TOKEN": "NGE3YjBkYjgtZDcwMy0zOTRhLWIzOWUtNTNhZGM5MTFmMzQ4OnRpZ2VydG9vdGhAY2FyYm9uLnN1cGVy"}

# req = requests.get(
#    configs["BASE_URL"] + "dining/menu",
#    params={ "locationId" : "0675", "menuID": "2019-03-15-LUNCH"},
#    headers={
#        "Authorization": "Bearer " + configs["ACCESS_TOKEN"]
#    },
# )
# text = req.text
# print(text)

app = Flask(__name__, template_folder='.')
app.static_folder = 'static'


# For all these functions, REFER to the FIGMA:
# https://www.figma.com/file/HkBlr87OPJfC8jKhJWQQDm/Prototype-Views?node-id=14%3A25


# For now, dining hall selection page
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    try:
        username = CASClient().authenticate()  # CAS
        html = render_template('index.html')
        response = make_response(html)
        return response
    except Exception as e:
        error_msg = e


# Reactions Page
@app.route('/reactions', methods=['GET', 'POST'])
def reactions():
    error_msg = ""
    # username = CASClient().authenticate()  # CAS
    if request.method == "POST":
        user_id = 2
        reaction = request.form['reaction']
        dhall = request.form['college']
        now = datetime.now()
        cur_time = now.strftime("%I:%M %p")
        data = (reaction, user_id, dhall, cur_time)
        try:
            database = Database()
            database.connect()
            database.reaction_submit(data)
            database.disconnect()
            # return redirect(url_for('/reactions-temp'), college=dhall)
            return redirect(request.referrer)
        except Exception as e:
            error_msg = e
    else:
        try:
            dhall = request.args.get("college")
            database = Database()
            database.connect()
            rows = database.get_reactions(dhall)
            database.disconnect()
            html = render_template('reactions.html', rows=rows, college=dhall)
            response = make_response(html)
            return response
        except Exception as e:
            error_msg = e


# @app.route('/reactions-temp', methods=['GET'])
# def temp():
#     print("in temp")
#     return redirect(url_for('/reactions', college=request.args.get("college")))


# Food Page
@app.route('/food', methods=['GET'])
def food():
    # username = CASClient().authenticate()  # CAS
    error_msg = ""
    try:
        dhall = request.args.get('college')
        ### Code for grabbing food from dining hall API ###
        request_lib = RequestsLib()
        # Get today's date
        today = datetime.datetime.today()
        year = str(today.year)

        # Pad the number with zeros so that
        # there are always exactly two digits
        month = str(today.month).zfill(2)
        day = str(today.day).zfill(2)

        # Get current time
        time_hour = datetime.datetime.now().hour
        meal = "Lunch"  # default value
        # breakfast, lunch, dinner
        if (time >= 5 and time < 10):
            meal = "Breakfast"
        elif (time >= 10 and time < 2):
            meal = "Lunch"
        elif (time >= 2 and time < 8):
            meal = "Dinner"

        # Get locationID
        locationID = 1
        if dhall == "wilcox":
            locationID = 1
        elif dhall == "forbes":
            locationID = 5
        elif dhall == "roma":
            locationID = 3
        elif dhall == "whitman":
            locationID = 6

        menu = request_lib.getJSON(
            request_lib.configs.DINING_MENU,
            locationID=locationID,
            menuID=year + "-" + month + "-" + day + "-" + meal,
        )
        menu_arr = menu['menus']
        database = Database()
        database.connect()
        foods = database.get_foods(dhall)
        database.disconnect()
        html = render_template('food.html', foods=foods,
                               college=dhall)
        response = make_response(html)
        return response
    except Exception as e:
        error_msg = e


# Food Item Description Page
@app.route('/food-desc', methods=['GET', 'POST'])
def food_desc():
    # username = CASClient().authenticate()  # CAS
    error_msg = ""
    # For posting reviews and 5-star ratings to database
    if request.method == "POST":
        user_id = 2
        rating = request.form['rating']
        review = request.form['review']
        if review == "":
            review = None
        food_id = request.form['food_id']
        now = datetime.now()
        cur_time = now.strftime("%I:%M %p")
        review_data = (user_id, food_id, review, rating, cur_time)
        try:
            database = Database()
            database.connect()
            database.add_review(review_data, rating, food_id)
            # UPDATE food SET num_rating = num_rating + 1, num_stars = num_stars + rating WHERE food.food_id = food_id
            database.disconnect()
            # return redirect(url_for('/reactions-temp'), college=dhall)
            return redirect(request.referrer)
        except Exception as e:
            error_msg = e
    # For reading existing reviews, the name/image of food, and description
    else:
        try:
            food_id = request.args.get("food_id")
            database = Database()
            database.connect()
            food = database.get_food_info(food_id)[0]
            reviews = database.get_reviews(food_id)
            database.disconnect()
            html = render_template(
                'food-desc.html', food=food, reviews=reviews, food_id=food_id)
            response = make_response(html)
            return response
        except Exception as e:
            error_msg = e


# @app.route('/logout', methods=['GET'])
# def logout():
 #   casClient = CASClient()
 #   casClient.authenticate()
 #   casClient.logout()
