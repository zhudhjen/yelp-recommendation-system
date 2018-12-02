import json
import os
import random

from flask import Flask, request, render_template, redirect, url_for, flash, send_file
from flask_bootstrap import Bootstrap


app = Flask(__name__)
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# app.secret_key = 'yelp recommendation system secret key'
Bootstrap(app)


rating_file = 'data/business_ratings.json'
recommendation_file = ''

recommended_business_ids = [
    'iCQpiavjjPzJ5_3gPD5Ebg',
    'Ums3gaP2qM3W1XcA5r6SsQ',
    'atVh8viqTj-sqDJ35tAYVg',
    'yEOu75XjwczngvWWlr0M_A',
    'alG1fb1kl2vmT8s34jbbHg',
    'd4z4gjdhQYs-WOVClISf_A',
    '7AlULGZI1pHt0imODsqdkg',
    'SpJYus_184M2TdT7t52rIA',
    'vsFFbN71ehRCp46KeR5RdQ',
    'YTbKmjGTdn4YzoJXTC1u7g'
]


# Load business ratings
business_ratings = {}
with open(rating_file, 'r') as f:
    for line in f:
        business = json.loads(line)
        business_ratings[business['business_id']] = business


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', post_flag=False)


@app.route('/', methods=['POST'])
def recommend():
    recommendations = [business_ratings[id] for id in recommended_business_ids]
    return render_template('index.html', recommendations=recommendations, post_flag=True)


@app.route('/statistics')
def statistics():
    return render_template('index.html', post_flag=False)


@app.route('/usages')
def usages():
    return render_template('usages.html')


@app.route('/links')
def links():
    return render_template('links.html')
