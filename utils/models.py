import copy
import json
import logging
from datetime import date
from typing import List, Tuple, Dict, Set

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
    def extract_user_ids(cls, reviews: 'List[Review]') -> 'Set[str]':
        users = set()
        for review in reviews:
            users.add(review.user_id)
        return users

    @classmethod
    def extract_business_ids(cls, reviews: 'List[Review]') -> 'Set[str]':
        businesses = set()
        for review in reviews:
            businesses.add(review.business_id)
        return businesses

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
    def extract_seen_reviews(cls, testing_reviews: 'List[Review]', seen_reviews: 'List[Review]') \
            -> 'Tuple[List[Review], List[Review]]':
        seen_user_set = set(Review.extract_user_ids(seen_reviews))
        seen_business_set = set(Review.extract_business_ids(seen_reviews))
        seen_reviews = []
        unseen_reviews = []

        for review in testing_reviews:
            if review.user_id in seen_user_set and review.business_id in seen_business_set:
                seen_reviews.append(copy.copy(review))
            else:
                unseen_reviews.append(copy.copy(review))

        return seen_reviews, unseen_reviews


class User:
    logger = logging.getLogger('models.User')

    def __init__(self, json_string=None) -> None:
        if json_string is not None:
            native_data = json.loads(json_string, encoding='UTF-8')
            self.user_id = native_data['user_id']
            self.name = native_data['name']
            self.avg_rating = float(native_data['average_stars'])
            self.review_count = native_data['review_count']
            self.useful = native_data['useful']
            self.funny = native_data['funny']
            self.cool = native_data['cool']
            self.fans = native_data['fans']
        else:
            self.user_id = "[not initialized]"
            self.name = "[not initialized]"
            self.avg_rating = -1.0
            self.review_count = -1
            self.useful = -1
            self.funny = -1
            self.cool = -1
            self.fans = -1
        self.features = ['NO_FEAT']

    @classmethod
    def load_from_file(cls, filename) -> 'Dict[str, User]':
        try:
            users: Dict[str, User] = {}
            with open(filename, 'r', encoding='UTF-8') as input_file:
                cls.logger.info('Loading reviews from: ' + filename)
                for line in input_file:
                    user = User(line)
                    users[user.user_id] = user
            return users
        except FileNotFoundError:
            cls.logger.error('Cannot load users from: ' + filename)
            return {}

    @classmethod
    def extract_user_ids(cls, users: 'Dict[str, User]') -> 'Set[str]':
        return set(users.keys())

    @classmethod
    def build_user_features(cls, users: 'Dict[str, User]',
                            selected_users: 'Set[str]' = None) -> List[Tuple[str, List[str]]]:
        if selected_users is None:
            keys = users.keys()
        else:
            keys = selected_users
        return list(map(lambda user_id: (user_id, users[user_id].features), keys))


class Business:
    logger = logging.getLogger('models.Business')

    def __init__(self, json_string=None) -> None:
        if json_string is not None:
            native_data = json.loads(json_string, encoding='UTF-8')
            self.business_id = native_data['business_id']
            self.name = native_data['name']
            self.avg_rating = float(native_data['stars'])
            self.review_count = native_data['review_count']
            self.categories = native_data['categories'] if native_data['categories'] is not None else []
            self.state = native_data['state']
        else:
            self.business_id = "[not initialized]"
            self.name = "[not initialized]"
            self.avg_rating = -1
            self.review_count = -1
            self.categories = []
            self.state = None
        self.features = []
        for category in self.categories:
            self.features.append('CAT_' + category)
        if self.state is not None:
            self.features.append('STATE_' + self.state)

    @classmethod
    def load_from_file(cls, filename) -> 'Dict[str, Business]':
        try:
            businesses: Dict[str, Business] = {}
            with open(filename, 'r', encoding='UTF-8') as input_file:
                cls.logger.info('Loading businesses from: ' + filename)
                for line in input_file:
                    business = Business(line)
                    businesses[business.business_id] = business
            return businesses
        except FileNotFoundError:
            cls.logger.error('Cannot load businesses from: ' + filename)
            return {}

    @classmethod
    def extract_business_ids(cls, businesses: 'Dict[str, Business]') -> 'Set[str]':
        return set(businesses.keys())

    @classmethod
    def collect_business_features(cls, businesses: 'Dict[str, Business]') -> 'Set[str]':
        features = set()
        for _, business in businesses.items():
            features = features.union(business.features)
        return features

    @classmethod
    def build_business_features(cls, businesses: 'Dict[str, Business]',
                                selected_businesses: 'Set[str]' = None) -> List[Tuple[str, List[str]]]:
        if selected_businesses is None:
            keys = businesses.keys()
        else:
            keys = selected_businesses
        return list(map(lambda businesses_id: (businesses_id, businesses[businesses_id].features), keys))
