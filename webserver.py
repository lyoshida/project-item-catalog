# coding: utf-8

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from flask import session as login_session
import random
import string

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Item

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


# Creating session and connection to DB
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)


@app.route('/login')
def login():
    """
        Renders login page and create a session variable (security)
    """
    state = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase) for x in xrange(32))
    login_session['state'] = state

    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
        User login with Google+
    """

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
    login_session['credentials'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    print credentials
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    print data

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    """
        Log out the user by removing session variables and revoking tokens.
    """

    access_token = login_session['credentials']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('index'))
    else:

        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
def index():
    """
        Renders main page
    """
    categories = session.query(Category).order_by('name')
    items = session.query(Item).order_by('-id')
    return render_template('index.html', categories=categories, items=items)


@app.route('/category/<int:category_id>')
def view_category(category_id):
    """
        Returns a page listing items for a given category.
    """
    category = session.query(Category).filter_by(id=category_id).one()
    categories = session.query(Category).order_by('name')

    items = session.query(Item).filter_by(category_id=category_id)

    return render_template('category_view.html',
                           categories=categories,
                           category=category,
                           items=items)


@app.route('/category/json')
def view_category_json():
    """
        Returns a list of categories in JSON format
    """
    categories = session.query(Category).order_by('name')

    return jsonify(items=[cat.serialize for cat in categories])


@app.route('/category/<int:category_id>/items/json')
def view_items_json(category_id):
    """
        Returns a list of items for a given category in JSON format
    """
    items = session.query(Item).filter_by(category_id=category_id)

    return jsonify(items=[item.serialize for item in items])


@app.route('/category/create', methods=['GET', 'POST'])
def create_category():
    """
        Form to create a new category
    """
    if request.method == 'GET':

        return render_template('category_create.html')

    else:

        if not request.form['category-name']:
            return render_template('category_create.html',
                                   error='Invalid input',
                                   message='Please enter a valid category.')
        else:
            new_category = Category(name=request.form['category-name'])
            session.add(new_category)
            session.commit()

            return redirect(url_for('index'))


@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
def edit_category(category_id):
    """
        Form to edit a new category
    """
    category = session.query(Category).filter_by(id=category_id).one()

    if request.method == 'GET':

        return render_template('category_edit.html',
                               category=category)

    else:

        if not request.form['category-name']:
            return render_template('category_edit.html',
                                   error='Invalid input',
                                   message='Please enter a valid category.')
        else:
            category.name = request.form['category-name']
            session.commit()

        return redirect(url_for('index'))


@app.route('/category/<int:category_id>/delete')
def delete_category(category_id):
    """
        Deletes a category
    """
    category = session.query(Category).filter_by(id=category_id).one()
    session.delete(category)
    session.commit()

    return redirect(url_for('index'))


@app.route('/item/<int:item_id>')
def view_item(item_id):
    """
        Show details for an item
    """
    categories = session.query(Category).order_by('name')
    item = session.query(Item).filter_by(id=item_id).one()
    category = session.query(Category).filter_by(id=item.category_id).one()

    return render_template('item_view.html',
                           item=item,
                           category=category,
                           categories=categories)


@app.route('/item/<int:item_id>/json')
def view_item_json(item_id):
    """
        Returns a list of items for a given category in JSON format
    """
    item = session.query(Item).filter_by(id=item_id).one()

    return jsonify(item.serialize)


@app.route('/category/<int:category_id>/item/create', methods=['GET', 'POST'])
def create_item(category_id):
    """
        Create a new item
    """
    category = session.query(Category).filter_by(id=category_id).one()

    if request.method == 'GET':

        return render_template('item_create.html',
                               category=category)

    else:

        if not request.form['item-name']:
            return render_template('item_create.html',
                                   error='Invalid input',
                                   message='Please enter a valid name.')
        else:
            new_item = Item(name=request.form['item-name'],
                            description=request.form['item-description'],
                            category_id=category_id)

            session.add(new_item)
            session.commit()

            return redirect(url_for('view_category', category_id=category_id))


@app.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
def edit_item(item_id):
    """
        Edit an item
    """
    item = session.query(Item).filter_by(id=item_id).one()

    if request.method == 'GET':

        return render_template('item_edit.html',
                               item=item)

    else:

        if not request.form['item-name']:
            return render_template('item_edit.html',
                                   error='Invalid input',
                                   message='Please enter a valid name.')
        else:
            item.name = request.form['item-name']
            item.description = request.form['item-description']
            session.commit()

        return redirect(url_for('index'))


@app.route('/item/<int:item_id>/delete')
def delete_item(item_id):
    """
        Delete an item
    """
    item = session.query(Item).filter_by(id=item_id).one()

    session.delete(item)
    session.commit()

    return redirect(url_for('view_category', category_id=item.category_id))


# Runs the server
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)