from flask import Flask, request, make_response, redirect, url_for
from flask import render_template
from database import Database
from datetime import datetime
# import requests

# please note: this is not a permanent access token... it needs to be refreshed a ton (1000 hrs)
# configs = {"BASE_URL": "https://api.princeton.edu/mobile-app/1.0.0/",
#    "ACCESS_TOKEN": "NGE3YjBkYjgtZDcwMy0zOTRhLWIzOWUtNTNhZGM5MTFmMzQ4OnRpZ2VydG9vdGhAY2FyYm9uLnN1cGVy"}

# req = requests.get(
#    configs["BASE_URL"] + "dining/menu",
#    params={ "locationId" : "0675", "menuID": "2019-03-15-LUNCH"},
#    headers={
#        "Authorization": "Bearer " + configs["ACCESS_TOKEN"]
#    },
#)
#text = req.text
#print(text)

app = Flask(__name__, template_folder='.')
app.static_folder = 'static'


# For all these functions, REFER to the FIGMA:
# https://www.figma.com/file/HkBlr87OPJfC8jKhJWQQDm/Prototype-Views?node-id=14%3A25


# For now, dining hall selection page
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    try:
        html = render_template('index.html')
        response = make_response(html)
        return response
    except Exception as e:
        error_msg = e


# Reactions Page
@app.route('/reactions', methods=['GET', 'POST'])
def reactions():
    error_msg = ""
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
    dhall = request.args.get('college')
    error_msg = ""
    try:
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
