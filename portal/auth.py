from flask import Flask, render_template, abort, request, url_for, Response, session, redirect, Blueprint, current_app
from datetime import date
from functools import wraps

bp = Blueprint('login_and_signup', __name__)

@bp.route('/signup', methods=['GET','POST'])
def signup():
    session.clear()

    return render_template('signup.jinja', title=f"{current_app.config['COMPANY_NAME']} - Signup Page")

@bp.route('/login', methods=['GET','POST'])
def login():
    session.clear()
    return render_template('login.jinja', title=f"{current_app.config['COMPANY_NAME']} - Login Page")

@bp.route('/', methods=['GET','POST'])
def default():
    session.clear()
    return render_template(current_app.config['DEFAULT_ENTRY_POINT']+ '.jinja', title=f"{current_app.config['COMPANY_NAME']} - " + str(current_app.config['DEFAULT_ENTRY_POINT']).capitalize() + " Page")

def authed(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):    
        if 'email' in request.form:
            for attribute in current_app.config["USER_ATTRIBUTES"]:
                session[attribute['var_name']] = request.form[attribute['var_name']]
            return f(*args, **kwargs)
        elif 'email' not in session:
            return redirect('/',307)
        else:
            return f(*args, **kwargs)
    return decorated_function