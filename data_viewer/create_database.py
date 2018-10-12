from yelp_metadata import load_session
from yelp_metadata import User, Business, Review
import json


INPUT_DIR = '../yelp_dataset/'
USER_FILE = INPUT_DIR + 'yelp_academic_dataset_user.json'
BUSINESS_FILE = INPUT_DIR + 'yelp_academic_dataset_business.json'
REVIEW_FILE = INPUT_DIR + 'yelp_academic_dataset_review.json'


if __name__ == '__main__':

    session = load_session()

    with open(USER_FILE) as f:
        for line in f:
            user = json.loads(line)
            session.add(User(user))
    session.commit()

    with open(BUSINESS_FILE) as f:
        for line in f:
            business = json.loads(line)
            session.add(Business(business))
    session.commit()

    with open(REVIEW_FILE) as f:
        count = 0
        for line in f:
            review = json.loads(line)
            session.add(Review(review))
            count += 1
            if count == 100000:
                count = 0
                session.commit()
    session.commit()
