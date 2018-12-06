import json

from flask import Flask, request, render_template, redirect, url_for, flash, send_file
from flask_bootstrap import Bootstrap


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = 'yelp recommendation system secret key'
Bootstrap(app)


rating_file = 'data/business_ratings.json'
review_count_file = 'data/business_review_count.json'
recommendation_file = 'data/lightfm_recommendations_full.json'


# Load business review count
business_review_count = {}
with open(review_count_file, 'r') as f:
    for line in f:
        review_count = json.loads(line)
        business_review_count[review_count['business_id']] = review_count['review_count']

# Load business rating and aspects statistics
business_ratings = {}
available_aspects = [[] for _ in range(6)]
with open(rating_file, 'r') as f:
    for line in f:
        business = json.loads(line)
        num = len([1 for value in business.values() if value != 'N/A']) - 1  # Remove the business_id
        available_aspects[num].append(business_review_count[business['business_id']])
        business_ratings[business['business_id']] = business

# Construct statistics data for doughnut chart
doughnut_data_nums = []
doughnut_data_review_count = []
for businesses in available_aspects:
    num = len(businesses)
    average = round(sum(businesses) / num, 2)
    doughnut_data_nums.append(num)
    doughnut_data_review_count.append(average)

# Load recommendation file
user_recommendations = {}
with open(recommendation_file, 'r') as f:
    recommendations = json.load(f)['recommendations']
for recommendation in recommendations:
    user_recommendations[recommendation['user_id']] = recommendation


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', post_flag=False)


@app.route('/', methods=['POST'])
def recommend():
    user_id = request.form['user_id']
    if user_id in user_recommendations:
        recommended_business_ids = user_recommendations[user_id]['recommended_businesses']
        recommended_businesses = [business_ratings[business_id] for business_id in recommended_business_ids]
        return render_template('index.html', recommendations=recommended_businesses, post_flag=True)
    else:
        return render_template('index.html', post_flag=False)


@app.route('/statistics')
def statistics():
    return render_template(
        'statistics.html',
        doughnut_data_nums=doughnut_data_nums,
        doughnut_data_review_count=doughnut_data_review_count
    )


@app.route('/usage')
def usage():
    return render_template('usage.html')


@app.route('/links')
def links():
    return render_template('links.html')
