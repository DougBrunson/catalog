import random
import requests
import json
import string
import httplib2
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, abort
from flask import session as login_session
from flask import make_response
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from db import Base, Item, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from functools import wraps

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "Airbnb"


# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def get_user_by_name(username):
    user = session.query(User).filter_by(name=username).one()
    return user


def authorized(host):
    current_user = login_session.get('username')
    return current_user == host


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


# Auth code from class
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        return redirect('/')
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response
    return redirect(url_for('index'))


@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/')
def index():
    logged_in = 'username' in login_session
    items = session.query(Item).all()
    return render_template('index.html', items=items, logged_in=logged_in)


@app.route('/new', methods=['POST', 'GET'])
@app.route('/item/new', methods=['POST', 'GET'])
@app.route('/item/new/', methods=['POST', 'GET'])
@login_required
def create():
    logged_in = 'username' in login_session
    if request.method == 'POST':
        item = Item(title=request.form['title'],
                    description=request.form['description'],
                    img_url=request.form['img_url'],
                    host=login_session['username'])
        session.add(item)
        session.commit()
        return redirect(url_for('index'))

    else:
        return render_template('new.html', logged_in=logged_in)


@app.route('/item/<int:item_id>')
@app.route('/item/<int:item_id>/')
def read(item_id):
    logged_in = 'username' in login_session
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('read.html', item=item, logged_in=logged_in)


@app.route('/item/<int:item_id>/edit', methods=['POST', 'GET'])
@app.route('/item/<int:item_id>/edit/', methods=['POST', 'GET'])
@login_required
def edit(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    logged_in = 'username' in login_session
    user_authed = authorized(item.host)

    if request.method == 'POST' and user_authed:
        item.title = request.form['title']
        item.description = request.form['description']
        item.img_url = request.form['img_url']

        session.add(item)
        session.commit()
        return redirect(url_for('index'))

    elif user_authed:
        return render_template('edit.html', item=item, logged_in=logged_in)
    else:
        abort(403)


@app.route('/item/<int:item_id>/delete', methods=['POST'])
@login_required
def delete(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    if 'username' in login_session and authorized(item.host):
        session.delete(item)
        session.commit()
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))


@app.route('/api/v1/item/<int:item_id>')
def api_item(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(item.serialize)


@app.route('/api/v1/item/all')
def api_all():
    items = session.query(Item).all()
    return jsonify(items=[i.serialize for i in items])


if __name__ == '__main__':
    app.secret_key = 'uB6YxmvEGccMqabK'
    app.run(host='0.0.0.0', debug=True)
