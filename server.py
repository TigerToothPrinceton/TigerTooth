from flask import Flask, request, make_response, redirect, url_for, jsonify
from flask import render_template, abort
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


# Landing Page
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    # try:
    username, err = CASClient().authenticate()  # CAS
    if not err:
        return redirect(url_for('dinhall'))
    try:
        database = Database()
        database.connect()
        database.add_user(username)
        database.disconnect()
    except Exception as e:
        error_msg = e
    html = render_template('index.html')
    response = make_response(html)
    return response
   # except Exception as e:
    # CASClient().authenticate() triggers an exception
   #  print("in the exception")
    # error_msg = e
   # print(error_msg)


# Dining hall selection page
@app.route('/dhall', methods=['GET'])
def dinhall():
    # try:
    username, err = CASClient().authenticate()  # CAS
    if err:
        return redirect(username)
    try:
        database = Database()
        database.connect()
        database.add_user(username)
        database.disconnect()
    except Exception as e:
        error_msg = e
    html = render_template('dhall.html')
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
    username, err = CASClient().authenticate()  # CAS
    if err:
        return redirect(username)
    if request.method == "POST":
        # Because data is JSON

        # Parse the JSON into a Python dictionary
        # print(request.form['reaction'])
        # req = request.get_json()
        # print(req)
        # reaction = req['reaction']
        # dhall = request['college']
        reaction = request.form['reaction']
        dhall = request.form['college']
        est = pytz.timezone('US/Eastern')
        now = datetime.now(est)
        hour = now.strftime("%-H")
        cur_time = now.strftime("%I:%M %p")
        # data = (reaction, user_id, dhall, cur_time)
        try:
            database = Database()
            database.connect()
            database.add_user(username)
            data = (reaction, username, dhall, cur_time, 20)
            database.add_reaction(data)
            database.disconnect()
            # return redirect(url_for('/reactions-temp'), college=dhall)
            # return redirect(request.referrer)

            # no need to return any html code bc only POSTing to DB
            # return '', 204

            # or return a confirmation
            return "Reaction successfully posted to DB"
        except Exception as e:
            error_msg = e
    if request.method == "GET":
        try:
            dhall = request.args.get("college")
            database = Database()
            database.connect()
            database.add_user(username)
            reactions = database.get_reactions(dhall)
            database.disconnect()
            html = ''
            for reaction in reactions:
                if reaction[1] != "":
                    html += '<div class="row align-items-center">'
                    if reaction[2] == username:
                        # html += '<div class = "col-3 col-sm-4 pt-2 pb-2" style = "font-size: 16px" >' + \
                        #     '<div class = "pBox" >' + reaction[4] + '</div >' + \
                        #     '</div>' + \
                        #     '<div class="col-9 col-sm-8 pt-2 pb-2 me-auto" style="font-size: 16px; ">' + \
                        #     '<div class="mymessage pBox" style = "text-align: right; margin-right: 0">' + \
                        #         reaction[1] + \
                        #     '</div>' + \
                        #     '</div>'
                        html += '<div class = "col-4 pt-2 pb-2" style = "font-size: 16px;">' + \
                            '<div class = "mymessagetime" style="padding-left: 10px; padding-bottom: 10px;">' + reaction[4] + '</div>' + \
                            '</div>' + \
                            '<div class="col-8 pt-2 pb-2" style="font-size: 16px;">' + \
                            '<div class="mymessage pBox">' + \
                                reaction[1] + \
                            '</div>' + \
                            '</div>'
                    else:
                        html += '<div class = "col-8 pt-2 pb-2" style = "font-size: 16px;"> <div class = "message pBox">' + \
                            reaction[1] + '</div></div><div class="col-4 pt-2 pb-2" style="font-size: 16px;"><div class = "messagetime" style="padding-right: 10px; padding-bottom: 10px;">' + \
                                reaction[4] + '</div></div>'
                    html += '</div>'
            # html = render_template('reactions.html', rows=rows, college=dhall)
            response = make_response(html)
            return response
        except Exception as e:
            error_msg = e
            html = render_template('error.html', message=error_msg)
            response = make_response(html)
            return response


# Food Page
@app.route('/food', methods=['GET', 'POST'])
def food():
    username, err = CASClient().authenticate()  # CAS
    if err:
        return redirect(username)
    error_msg = ""
    if request.method == "POST":
        rating = request.form['rate']
        if rating == 0 or rating is None:
            html = render_template(
                'error.html', message="Please submit a rating")
            response = make_response(html)
            return response
        review = request.form['review']
        if review == "":
            review = None
        food_id = request.form['food_id']
        est = pytz.timezone('US/Eastern')
        now = datetime.now(est)
        cur_time = now.strftime("%I:%M %p")
        try:
            database = Database()
            database.connect()
            database.add_user(username)
            review_data = (username, food_id, review, rating, cur_time)
            database.add_review(review_data, rating, food_id)
            database.disconnect()
            # return redirect(request.referrer)
            return "Rating and review successfully posted to DB"
        except Exception as e:
            error_msg = e
            html = render_template('error.html', message=error_msg)
            response = make_response(html)
            return response
    if request.method == 'GET': 
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
            #database.clear_db(meal)
            database.add_user(username)
            # add new foods to the database if they do not exist
            database.add_food(menu_arr, dhall)

            foods = []
            reviews = []
            # grab the foods being served at the dhall with the same api_id as the dhall api
            for food in menu_arr:
                api_id = food['id']
                result = database.get_food(api_id, dhall)
                foods.append(result)
                food_id = database.get_food(api_id, dhall)[4]
                review = database.get_reviews(food_id)
                reviews.append(review)
            rows = database.get_reactions(dhall)

            database.disconnect()
            html = render_template('food.html', foods=foods, rows=rows,
                                   college=dhall, meal_time=meal, username=username, reviews=reviews)
            response = make_response(html)
            return response
        except Exception as e:
            html = render_template(
                'error.html', message="Look's like our menu is unavailable. Please try again later!")
            response = make_response(html)
            return response


# Food Item Description Page
@app.route('/food-desc', methods=['GET'])
def food_desc():
    username, err = CASClient().authenticate()  # CAS
    if err:
        return redirect(username)
    error_msg = ""
    # For reading existing reviews, the name/image of food, and description
    try:
        food_id = request.args.get("food_id")
        college = request.args.get("college")
        database = Database()
        database.connect()
        database.add_user(username)
        food = database.get_food_info(food_id)[0]
        # reviews = database.get_reviews(food_id)
        database.disconnect()
        html = render_template(
            'food-desc.html', college=college, food=food, food_id=food_id)
        response = make_response(html)
        return response
    except Exception as e:
        error_msg = e


# Food Item Description Page for JQuery AJAX calls
@app.route('/food-updates', methods=['GET', 'POST'])
def food_updates():
    username, err = CASClient().authenticate()  # CAS
    if err:
        return redirect(username)
    error_msg = ""
    # For posting reviews and 5-star ratings to database
    if request.method == "POST":
        rating = request.form['rate']
        if rating == 0 or rating is None:
            html = render_template(
                'error.html', message="Please submit a rating")
            response = make_response(html)
            return response
        review = request.form['review']
        if review == "":
            review = None
        food_id = request.form['food_id']
        est = pytz.timezone('US/Eastern')
        now = datetime.now(est)
        cur_time = now.strftime("%I:%M %p")
        try:
            database = Database()
            database.connect()
            database.add_user(username)
            review_data = (username, food_id, review, rating, cur_time)
            database.add_review(review_data, rating, food_id)
            database.disconnect()
            # return redirect(request.referrer)
            return "Rating and review successfully posted to DB"
        except Exception as e:
            error_msg = e
            html = render_template('error.html', message=error_msg)
            response = make_response(html)
            return response
    # For reading existing reviews, the name/image of food, and description
    else:
        try:
            food_id = request.args.get("food_id")
            college = request.args.get("college")

            database = Database()
            database.connect()
            database.add_user(username)
            food = database.get_food_info(food_id)[0]
            reviews = database.get_reviews(food_id)
            database.disconnect()

            if food[2] == 0:
                the_rating = '<p style="margin: 10px 0;"> Rating: No Rating Yet!</p>'
            else:
                rating = round((food[3]/food[2]), 1)
                the_rating = '<p style = "margin: 10px 0;"> Rating: ' + \
                    str(rating) + '</p>'

            html = ''
            if len(reviews) == 0 or reviews[0][0] == None:
                html += '<div class = "col-3" ></div>' + \
                    '<div class = "col-6 pr-1 pl-1" style = "border:2px solid #000000; border-radius: 0.4rem;">' + \
                    '<p style = "font-size: 16px; text-align:center; margin: 10px"> No reviews submitted yet! Be the first to review!</p>' + \
                    '</div>' + \
                    '<div class = "col-3"></div>'
            else:
                html += '<div class="col-2"></div>' + \
                    '<div class="col-8 pl-1 pr-1 pt-1 pb-1" style="border:2px solid #000000; border-radius: 0.4rem; min-height: 15vh; max-height:30vh; overflow: auto" id="reviews-box">'

                for review in reviews:
                    if review[0] is not None:
                        html += '<div class="row border-bottom align-items-center">' + \
                                '<div class="col" style="font-size: 16px;">' + \
                            review[0] + \
                                '</div>' + \
                            '</div>'

                html += '</div>' + \
                        '<div class="col-2"></div>'

            # for review in reviews:
            #     if review[0] is not None:
            #         html += '<div class="row border-bottom align-items-center">' + \
            #                 '<div class="col" style="font-size: 16px;">' + \
            #             review[0] + \
            #                 '</div>' + \
            #             '</div >'

            response_body = {
                "food_rating": the_rating,
                "reviews": html,
            }
            response = make_response(jsonify(response_body), 200)
            return response
        except Exception as e:
            error_msg = e


# Submit a Photo URL to a Food Item
@app.route('/foodimg-submit', methods=['GET', 'POST'])
def food_img_submit():
    username, err = CASClient().authenticate()  # CAS
    if err:
        return redirect(username)
    database = Database()
    database.connect()
    database.add_user(username)
    database.disconnect()
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


# User Past Reviews Page
@app.route('/history', methods=['GET'])
def history():
    username, err = CASClient().authenticate()  # CAS
    if err:
        return redirect(username)
    try:
        database = Database()
        database.connect()
        reviews = database.get_history(username)
        database.disconnect()
        html = render_template('history.html', reviews=reviews)
        response = make_response(html)
        return response
    except Exception as e:
        print(e)
        html = render_template(
            'error.html', message="Look's like your history is unavailable. Please try again later!")
        response = make_response(html)
        return response


@app.route('/logout', methods=['GET'])
def logout():
    casClient = CASClient()
    casClient.authenticate()
    casClient.logout()
