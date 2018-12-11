from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash, g
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, CategoryItem, User
from flask import session as login_session
from functools import wraps
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"

# Connect to Database and create database session
engine = create_engine('sqlite:///catalogs.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


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
        return response

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

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already \
            connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
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
    output += ' " style = "width: 200px; height: 200px;border-radius: \
    150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
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
    except BaseException:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # If the given token was invalid notice the user.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Catalog Information
@app.route('/catalogs/JSON')
def catalogJSON():
    categorieslist = session.query(Catalog).all()
    return jsonify(CategoriesList=[r.serialize for r in categorieslist])


@app.route('/catalogs/<int:categories_id>/JSON')
def categoryJSON(categories_id):
    categories = session.query(Catalog).filter_by(id=categories_id).one()
    items = session.query(CategoryItem).filter_by(categories_id=categories.id)
    return jsonify(CategoryItem=[i.serialize for i in items])


@app.route('/catalogs/<int:categories_id>/<int:items_id>/JSON')
def itemJSON(categories_id, items_id):
    categories = session.query(Catalog).filter_by(id=categories_id).one()
    items = session.query(CategoryItem).filter_by(id=items_id).one()
    return jsonify(ItemDetails=[items.serialize])


# Login Required function
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("You are not allowed to access there")
            return redirect('/login')
    return decorated_function


@app.route('/')
@app.route('/catalogs')
def showCatalog():
    catalog = session.query(Catalog).all()
    items = session.query(CategoryItem).order_by(
        CategoryItem.id.desc())
    if 'username' not in login_session:
        return render_template('publiccatalog.html', catalog=catalog,
                               items=items)
    else:
        return render_template('catalog.html', catalog=catalog,
                               items=items)


# Create new item
@app.route('/catalogs/new', methods=['GET', 'POST'])
@login_required
def newItem():
    if request.method == 'POST':
        newItem = CategoryItem(name=request.form['name'],
                               description=request.form['description'],
                               categories_id=request.form['categories_id'],
                               user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash("* New Item Successfully Created *")
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newitem.html')


# Display items inside the category
@app.route('/catalogs/<int:categories_id>')
def showCategories(categories_id):
    allcategories = session.query(Catalog).all()
    catalog = session.query(Catalog).filter_by(id=categories_id).one()
    items = session.query(CategoryItem).filter_by(categories_id=catalog.id)
    return render_template('category.html', catalog=catalog, items=items,
                           allcategories=allcategories)


# Display the specific item and the description of it
@app.route('/catalogs/<int:categories_id>/<int:items_id>')
def showItem(categories_id, items_id):
    categories = session.query(Catalog).filter_by(id=categories_id).one()
    items = session.query(CategoryItem).filter_by(id=items_id).one()
    if 'username' not in login_session or \
            items.user_id != login_session['user_id']:

        return render_template('publicitem.html', categories=categories,
                               items=items)
    else:
        return render_template('item.html', categories=categories, items=items)


# Edit the specific item
@app.route('/catalogs/<int:categories_id>/<int:items_id>/edit',
           methods=['GET', 'POST'])
@login_required
def editCategories(categories_id, items_id):
    editedItem = session.query(CategoryItem).filter_by(id=items_id).one()

    if editedItem.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized"\
            "to edit this item. Please create your own item in order to edit"\
            ".');window.location = '/';}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name'] == "":
            editedItem.name = editedItem.name
        else:
            editedItem.name = request.form['name']
        if request.form['description'] == "":
            editedItem.description = editedItem.description
        else:
            editedItem.description = request.form['description']
        if request.form['categories_id'] == "":
            editedItem.categories_id = editedItem.categories_id
        else:
            editedItem.categories_id = request.form['categories_id']

        session.add(editedItem)
        session.commit()
        flash("Item Successfully Edited!")
        return redirect(url_for('showItem', categories_id=categories_id,
                                items_id=items_id))
    else:
        return render_template('edititem.html', categories_id=categories_id,
                               items_id=items_id, item=editedItem)


# Delete the specific item
@app.route('/catalogs/<int:categories_id>/<int:items_id>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteCategories(categories_id, items_id):
    itemToDelete = session.query(CategoryItem).filter_by(id=items_id).one()

    if itemToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized "\
            "to delete this item. Please create your own item to delete. "\
            "');window.location = '/';}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("Item Successfully Deleted!")
        return redirect(url_for('showCategories', categories_id=categories_id))
    else:
        return render_template('deleteitem.html', categories_id=categories_id,
                               items_id=items_id, item=itemToDelete)


# disconnect from the login session
@app.route('/disconnect')
def disconnect():
    if 'username' in login_session:
        gdisconnect()
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatalog'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
