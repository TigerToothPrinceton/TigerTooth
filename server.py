from flask import Flask, request, make_response, redirect, url_for
from flask import render_template
from database import Database


app = Flask(__name__, template_folder='.')


# For all these functions, REFER to the FIGMA:
# https://www.figma.com/file/HkBlr87OPJfC8jKhJWQQDm/Prototype-Views?node-id=14%3A25


# For now, dining hall selection page
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    dept = request.args.get('dept')
    number = request.args.get('number')
    area = request.args.get('area')
    title = request.args.get('title')

    if dept is None:
        dept = ''
    if number is None:
        number = ''
    if area is None:
        area = ''
    if title is None:
        title = ''

    form_args = [dept, number, area, title]
    error_msg = ""
    try:
        database = Database()
        database.connect()
        rows = database.search(form_args)
        database.disconnect()
    except Exception as e:
        error_msg = e
        rows = []

    html = render_template('index.html', error_msg=error_msg, dept=dept,
                           number=number, area=area, title=title, rows=rows)
    response = make_response(html)
    response.set_cookie('prev_dept', dept)
    response.set_cookie('prev_num', number)
    response.set_cookie('prev_area', area)
    response.set_cookie('prev_title', title)
    return response


# Reactions Page
@app.route('/reaction', methods=['GET'])
def reactions():
    classid = request.args.get('classid')
    is_int = True

    try:
        int(classid)
    except:
        is_int = False

    prev_dept = request.cookies.get('prev_dept')
    prev_num = request.cookies.get('prev_num')
    prev_area = request.cookies.get('prev_area')
    prev_title = request.cookies.get('prev_title')

    error_msg = ""
    try:
        database = Database()
        database.connect()
        results = database.class_details(classid)
        database.disconnect()
    except Exception as e:
        error_msg = e
        results = {}

    html = render_template('classdetails.html', error_msg=error_msg, is_int=is_int, results=results, classid=classid,
                           prev_dept=prev_dept, prev_num=prev_num, prev_area=prev_area, prev_title=prev_title)
    response = make_response(html)
    return response


# Food Page
@app.route('/food', methods=['GET'])
def dhall():
    return


# Food Item Description Page
@app.route('/food-desc', methods=['GET'])
def food_desc():
    return
