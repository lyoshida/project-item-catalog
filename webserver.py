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

    categories = session.query(Category).order_by('name')
    items = session.query(Item).order_by('-id')
    return render_template('index.html', categories=categories, items=items)


@app.route('/category/<int:category_id>')
def view_category(category_id):

    category = session.query(Category).filter_by(id=category_id).one()
    categories = session.query(Category).all()

    items = session.query(Item).filter_by(category_id=category_id)

    return render_template('category_view.html',
                           categories=categories,
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


@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
def edit_category(category_id):

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

    category = session.query(Category).filter_by(id=category_id).one()
    session.delete(category)
    session.commit()

    return redirect(url_for('index'))


@app.route('/item/<int:item_id>')
def view_item(item_id):
    categories = session.query(Category).all()
    item = session.query(Item).filter_by(id=item_id).one()
    category = session.query(Category).filter_by(id=item.category_id).one()

    return render_template('item_view.html',
                           item=item,
                           category=category,
                           categories=categories)


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


@app.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
def edit_item(item_id):
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

    item = session.query(Item).filter_by(id=item_id).one()

    session.delete(item)
    session.commit()

    return redirect(url_for('view_category', category_id=item.category_id))


# Runs the server
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)