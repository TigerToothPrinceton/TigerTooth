from flask import Flask, request, make_response, redirect, url_for
from flask import render_template
from database import Database
from datetime import datetime


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
    print(request.method)
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
        print(foods)
        database.disconnect()
        html = render_template('food.html', foods=foods, college=dhall)
        response = make_response(html)
        return response
    except Exception as e:
        error_msg = e


# Food Item Description Page
@app.route('/food-desc', methods=['GET', 'POST'])
def food_desc():
    error_msg = ""
    print(request.method)
    if request.method == "POST":
        user_id = 2
        review = request.form['review']
        dhall = request.form['name']
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
            name = request.args.get("name")
            database = Database()
            database.connect()
            rows = database.get_foodInfo(name)
            database.disconnect()
            html = render_template('food-desc.html', foods=foods, college=name)
            response = make_response(html)
            return response
        except Exception as e:
            error_msg = e






