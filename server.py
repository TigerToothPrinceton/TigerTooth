from flask import Flask, request, make_response, redirect, url_for
from flask import render_template
from database import Database
from datetime import datetime
from CASClient import CASClient
from requests_lib import RequestsLib
import pytz


### IMPORTANT: Dining Hall Menu only keeps 2 weeks of data ###

app = Flask(__name__, template_folder='.')
app.static_folder = 'static'

app.secret_key = b'!\xcf]\x90\xa9\x00\xefsl\xb3<\xb43]\xfc\x88'

# For all these functions, REFER to the FIGMA:
# https://www.figma.com/file/HkBlr87OPJfC8jKhJWQQDm/Prototype-Views?node-id=14%3A25


# For now, dining hall selection page
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    # try:
    username = CASClient().authenticate()  # CAS
    html = render_template('index.html')
    response = make_response(html)
    return response
   # except Exception as e:
    # CASClient().authenticate() triggers an exception
   #  print("in the exception")
    # error_msg = e
   # print(error_msg)


# Reactions Page
@app.route('/reactions', methods=['GET', 'POST'])
def reactions():
    error_msg = ""
    username = CASClient().authenticate()  # CAS
    if request.method == "POST":
        user_id = 2
        reaction = request.form['reaction']
        dhall = request.form['college']
        est = pytz.timezone('US/Eastern')
        now = datetime.now(est)
        cur_time = now.strftime("%I:%M %p")
        data = (reaction, user_id, dhall, cur_time)
        try:
            database = Database()
            database.connect()
            database.add_reaction(data)
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
    username = CASClient().authenticate()  # CAS
    error_msg = ""
    try:
        dhall = request.args.get('college')
        # dhall = request.args['college']
        ### Code for grabbing food from dining hall API ###
        request_lib = RequestsLib()

        # timezone
        est = pytz.timezone('US/Eastern')
        # Get today's date
        today = datetime.today().astimezone(est)
        year = str(today.year)

        # Pad the number with zeros so that
        # there are always exactly two digits
        month = str(today.month).zfill(2)
        day = str(today.day).zfill(2)

        # Get current time
        time_hour = datetime.now(est).hour
        meal = "Lunch"  # default value, case-sensitive
        # breakfast, lunch, dinner
        if (time_hour >= 5 and time_hour < 10):
            meal = "Breakfast"
        elif (time_hour >= 10 and time_hour < 14):
            meal = "Lunch"
        elif (time_hour >= 14 and time_hour < 20):
            meal = "Dinner"
        database.clear_db(meal)
            
        # Get locationID
        locationID = 1
        if dhall == "wilcox":
            locationID = 1
        elif dhall == "forbes":
            locationID = 5
        elif dhall == "roma":
            locationID = 4
        elif dhall == "whitman":
            locationID = 6

        # make a call to dining hall api and grab all the items in the current meal menu
        menu = request_lib.getJSON(
            request_lib.configs.DINING_MENU,
            locationID=locationID,
            menuID=year + "-" + month + "-" + day + "-" + meal,
        )
        menu_arr = menu['menus']
        database = Database()
        database.connect()
        # add new foods to the database if they do not exist
        database.add_food(menu_arr, dhall)

        foods = []
        # grab the foods being served at the dhall with the same api_id as the dhall api
        for food in menu_arr:
            api_id = food['id']
            result = database.get_food(api_id, dhall)
            foods.append(result)

        database.disconnect()
        html = render_template('food.html', foods=foods,
                               college=dhall, meal_time=meal)
        response = make_response(html)
        return response
    except Exception as e:
        print(e)
        error_msg = e


# Food Item Description Page
@app.route('/food-desc', methods=['GET', 'POST'])
def food_desc():
    username = CASClient().authenticate()  # CAS
    error_msg = ""
    # For posting reviews and 5-star ratings to database
    if request.method == "POST":
        user_id = 2
        rating = request.form['rating']
        review = request.form['review']
        if review == "":
            review = None
        food_id = request.form['food_id']
        est = pytz.timezone('US/Eastern')
        now = datetime.now(est)
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
            college = request.args.get("college")
            database = Database()
            database.connect()
            food = database.get_food_info(food_id)[0]
            reviews = database.get_reviews(food_id)
            database.disconnect()
            html = render_template(
                'food-desc.html', college=college, food=food, reviews=reviews, food_id=food_id)
            response = make_response(html)
            return response
        except Exception as e:
            error_msg = e


# Submit a Photo URL to a Food Item
@app.route('/foodimg-submit', methods=['GET', 'POST'])
def food_img_submit():
    username = CASClient().authenticate()  # CAS
    error_msg = ""
    if request.method == "POST":
        try:
            api_id = request.form['api_id']
            food_url = request.form['food_url'] + '.jpg'
            dhall = request.form['college']
            database = Database()
            database.connect()
            database.add_food_image(api_id, food_url)
            database.disconnect()
            return redirect(url_for('food', college=dhall))
        except Exception as e:
            print(e)
            error_msg = e
    else:
        try:
            api_id = request.args.get("api_id")
            dhall = request.args.get("college")
            html = render_template(
                'foodimg-submit.html', api_id=api_id, college=dhall)
            response = make_response(html)
            return response
        except Exception as e:
            print(e)
            error_msg = e


@app.route('/logout', methods=['GET'])
def logout():
    casClient = CASClient()
    casClient.authenticate()
    casClient.logout()
