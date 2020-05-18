# coding=utf-8

from flask import Flask, render_template, flash, redirect, session, url_for, request, g, Markup
from app import app
# from pymongo import MongoClient

# @app.route('/')
# @app.route('/index')
# def index():
#     return render_template('index.html')

# client = MongoClient('localhost', 27017)
# db = client.tododb

# @app.route('/test-db')
# def todo():

#  _items = db.tododb.find()
#  items = [item for item in _items]
#  return render_template('todo.html', items=items)

# @app.route('/new', methods=['POST'])
# def new():

#  item_doc = {
#    'task': request.form['task'],
#    'description': request.form['description']
#  }
#  db.tododb.insert_one(item_doc)

#  return redirect(url_for('todo'))

@app.route('/about')
def about():
    return render_template('about.html')
    