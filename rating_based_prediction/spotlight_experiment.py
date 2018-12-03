import math
import sys
import time
from typing import List

import numpy as np
from sklearn.metrics import mean_squared_error, roc_auc_score
from spotlight.factorization.implicit import ImplicitFactorizationModel
from spotlight.interactions import Interactions

from utils.models import Review

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 spotlight_experiment.py <PATH_TO_TRAINING_SET> <PATH_TO_TESTING_SET>")
        exit(1)

    start_time = time.time()

    training_set_file = sys.argv[1]
    testing_set_file = sys.argv[2]

    print('[ %04ds ] Program started' % (time.time() - start_time))

    training_set: List[Review] = Review.load_from_file(training_set_file)
    user_avg, user_std = Review.extract_user_average_and_std(training_set)
    normalized_training_reviews = Review.normalize_by_user(training_set, user_avg)
    raw_training_interactions = Review.extract_sparse_interaction_matrix(normalized_training_reviews)

    print('[ %04ds ] Dataset loaded' % (time.time() - start_time))

    user_ids = []
    user_id_map = {}
    training_user_ids = []
    business_ids = []
    business_id_map = {}
    training_business_ids = []
    training_ratings = []

    for pair in raw_training_interactions:
        user, business, rating = pair
        if user not in user_id_map:
            user_id_map[user] = len(user_ids)
            user_ids.append(user)
        if business not in business_id_map:
            business_id_map[business] = len(business_ids)
            business_ids.append(business)

        training_user_ids.append(user_id_map[user])
        training_business_ids.append(business_id_map[business])
        training_ratings.append(rating)

    print('[ %04ds ] Mapping created' % (time.time() - start_time))

    training_interactions = Interactions(np.array(training_user_ids),
                                         np.array(training_business_ids),
                                         np.array(training_ratings, dtype=np.float32))

    no_components = 30
    loss = 'pointwise'
    batch_size = 64
    learning_rate = 0.1
    l2 = 1e-7
    epochs = 8

    model = ImplicitFactorizationModel(loss=loss, embedding_dim=no_components, learning_rate=learning_rate,
                                       batch_size=batch_size, n_iter=epochs, l2=l2)

    model.fit(training_interactions, verbose=True)
    print('[ %04ds ] Model fitted' % (time.time() - start_time))

    testing_set: List[Review] = Review.load_from_file(testing_set_file)
    seen_testing_set, unseen_testing_set = Review.extract_seen_reviews(testing_set, training_set)
    print(len(seen_testing_set), len(unseen_testing_set))
    normalized_seen_testing_set = Review.normalize_by_user(seen_testing_set, user_avg)
    seen_pairs, ground_truth = Review.extract_sparse_testing_matrix_and_ground_truth(normalized_seen_testing_set)
    testing_user_ids = []
    testing_business_ids = []
    for user, business in seen_pairs:
        testing_user_ids.append(user_id_map[user])
        testing_business_ids.append(business_id_map[business])

    predictions = model.predict(np.array(testing_user_ids), np.array(testing_business_ids))
    # min_pred = np.min(predictions)
    # max_pred = np.max(predictions)
    # normalized_predictions = (np.array(predictions) - min_pred) / (max_pred - min_pred) * 4 + 1

    auc = roc_auc_score(np.array(ground_truth) >= 0, predictions)
    rmse = math.sqrt(mean_squared_error(ground_truth, predictions))

    print('[ %04ds ] Finished' % (time.time() - start_time))

    print("AUC = %.4f" % auc)
    print("RMSE = %.4f" % rmse)
