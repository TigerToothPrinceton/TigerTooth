from flask import Flask, request, make_response, redirect, url_for
from flask import render_template
from database import Database
from datetime import datetime


app = Flask(__name__, template_folder='.')


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
@app.route('/reaction', methods=['GET', 'POST'])
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
            return redirect(url_for('/reaction?college={}'.format(college)))
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


# # Food Page (HELLLLLLLLP)
# @app.route('/food', methods=['GET'])
  def food():
    error_msg = ""
    user_id = 2
    reaction = request.form['reaction']
    dhall = request.form['college']\
    data = (reaction, user_id, dhall, cur_time)
    try:
        database = Database()
        database.connect()
        database.reaction_submit(data)
        database.disconnect()
        return redirect(url_for('/reaction?college={}'.format(college)))
    except Exception as e:
        error_msg = e



# # Food Item Description Page
# @app.route('/food-desc', methods=['GET'])
# def food_desc():
#     return
