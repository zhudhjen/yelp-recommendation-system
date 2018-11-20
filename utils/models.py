import copy
import json
import logging
from datetime import date
from typing import List, Tuple, Dict

import numpy as np


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
            self.text = native_review['text']
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
            with open(filename, 'r', encoding='UTF-8') as input_file:
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
        users = set()
        for review in reviews:
            users.add(review.user_id)
        return list(users)

    @classmethod
    def extract_business_ids(cls, reviews: 'List[Review]') -> 'List[str]':
        businesses = set()
        for review in reviews:
            businesses.add(review.business_id)
        return list(businesses)

    @classmethod
    def extract_sparse_interaction_matrix(cls, reviews: 'List[Review]') -> 'List[Tuple[str, str, float]]':
        return list(map(lambda review: (review.user_id, review.business_id, review.rating), reviews))

    @classmethod
    def extract_sparse_testing_matrix_and_ground_truth(cls, reviews: 'List[Review]') \
            -> 'Tuple[List[Tuple[str, str]], List[float]]':

        return list(map(lambda review: (review.user_id, review.business_id), reviews)), \
               list(map(lambda review: review.rating, reviews))

    @classmethod
    def extract_user_average_and_std(cls, reviews: 'List[Review]') -> 'Tuple[Dict[str, float], Dict[str, float]]':
        user_ratings = {}
        for review in reviews:
            if review.user_id not in user_ratings:
                user_ratings[review.user_id] = []
            user_ratings[review.user_id].append(review.rating)

        user_avg = {}
        user_std = {}
        for user, ratings in user_ratings.items():
            user_avg[user] = float(np.mean(ratings))
            user_std[user] = float(np.std(ratings))

        return user_avg, user_std

    @classmethod
    def normalize_by_user(cls, reviews: 'List[Review]', user_avg: Dict[str, float] = None,
                          user_std: Dict[str, float] = None) -> 'List[Review]':
        updated_reviews = []
        for review in reviews:
            normalized_review = copy.copy(review)
            rating = review.rating
            avg = user_avg[review.user_id]
            std = user_std[review.user_id] if user_std is not None else 0
            normalized_review.rating = rating - avg if std == 0 else (rating - avg) / std
            updated_reviews.append(normalized_review)

        return updated_reviews

    @classmethod
    def extract_seen_reviews(cls, testing_reviews: 'List[Review]', seen_reviews: 'List[Review]') -> 'List[Review]':
        seen_user_set = set(Review.extract_user_ids(seen_reviews))
        seen_business_set = set(Review.extract_business_ids(seen_reviews))
        intersection = []

        for review in testing_reviews:
            if review.user_id in seen_user_set and review.business_id in seen_business_set:
                intersection.append(copy.copy(review))

        return intersection
