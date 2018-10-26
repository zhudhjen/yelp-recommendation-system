import json
import logging
from collections import Set
from datetime import date
from typing import List, Tuple


class Review:
    logger = logging.getLogger('models.Review')

    def __init__(self, json_string=None) -> None:
        if json_string is not None:
            native_review = json.loads(json_string, encoding='UTF-8')
            self.review_id = native_review['review_id']
            self.user_id = native_review['user_id']
            self.business_id = native_review['business_id']
            self.rating = float(native_review['stars'])
            date_parts = native_review['date'].split('-')
            self.date = date(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
            self.text = native_review['review']
        else:
            self.review_id = "[not initialized]"
            self.user_id = "[not initialized]"
            self.business_id = "[not initialized]"
            self.rating = -1.0
            self.date = date.fromordinal(0)
            self.text = "[not initialized]"

    def get_review_id(self) -> str:
        return self.review_id

    def get_user_id(self) -> str:
        return self.user_id

    def get_business_id(self) -> str:
        return self.business_id

    def get_rating(self) -> float:
        return self.rating

    def set_rating(self, new_rating) -> None:
        self.rating = new_rating

    def get_text(self):
        return self.text

    @classmethod
    def load_from_file(cls, filename) -> 'List[Review]':
        try:
            reviews: List[Review] = []
            with open(filename, 'r') as input_file:
                cls.logger.info('Loading reviews from: ' + filename)
                for line in input_file:
                    review = Review(line)
                    reviews.append(review)
            return reviews
        except FileNotFoundError:
            cls.logger.error('Cannot load reviews from: ' + filename)
            return []

    @classmethod
    def extract_user_ids(cls, reviews: 'List[Review]') -> 'List[str]':
        users = Set()
        for review in reviews:
            users += review.user_id
        return list(users)

    @classmethod
    def extract_business_ids(cls, reviews: 'List[Review]') -> 'List[str]':
        users = Set()
        for review in reviews:
            users += review.business_id
        return list(users)

    @classmethod
    def extract_sparse_interaction_matrix(cls, reviews: 'List[Review]') -> 'List[Tuple[str, str, float]]':
        return list(map(lambda review: (review.user_id, review.business_id, review.rating), reviews))

# TODO: Create classes for users and businesses
