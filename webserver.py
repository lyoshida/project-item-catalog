from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Item


# Creating session and connection to DB
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


app = Flask(__name__)


@app.route('/')
def index():

    categories = session.query(Category).all()
    return render_template('index.html', categories=categories)


@app.route('/category/<int:category_id>')
def view_category(category_id):

    category = session.query(Category).filter_by(id=category_id).one()

    items = session.query(Item).filter_by(category_id=category_id)

    return render_template('category_view.html',
                           category=category,
                           items=items)


@app.route('/category/create', methods=['GET', 'POST'])
def create_category():

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


@app.route('/category/<int:category_id>/edit')
def edit_category():
    return render_template('category_edit.html')


@app.route('/category/<int:category_id>/delete')
def delete_category():
    pass


@app.route('/item/<int:item_id>')
def view_item(item_id):

    item = session.query(Item).filter_by(id=item_id).one()

    return render_template('item_view.html',
                           item=item)

@app.route('/category/<int:category_id>/item/create', methods=['GET', 'POST'])
def create_item(category_id):

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


@app.route('/category/<int:category_id>/item/edit')
def edit_item():
    return render_template('item_edit.html')


@app.route('/item/<int:item_id>/delete')
def delete_item():
    pass




# Runs the server
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)