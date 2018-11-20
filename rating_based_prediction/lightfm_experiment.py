import math
import sys
import time
from typing import List

import numpy as np
from lightfm import LightFM
from lightfm.data import Dataset
from sklearn.metrics import mean_squared_error, roc_auc_score

from utils.models import Review

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 lightfm_experiment.py <PATH_TO_TRAINING_SET> <PATH_TO_TESTING_SET>")
        exit(1)

    start_time = time.time()

    training_set_file = sys.argv[1]
    testing_set_file = sys.argv[2]

    print('[ %04ds ] Program started' % (time.time() - start_time))

    training_set: List[Review] = Review.load_from_file(training_set_file)
    user_avg, user_std = Review.extract_user_average_and_std(training_set)
    normalized_training_reviews = Review.normalize_by_user(training_set, user_avg)
    training_interactions = Review.extract_sparse_interaction_matrix(normalized_training_reviews)
    training_user_ids = Review.extract_user_ids(normalized_training_reviews)
    training_business_ids = Review.extract_business_ids(normalized_training_reviews)

    dataset = Dataset()
    dataset.fit(training_user_ids, training_business_ids)
    print('[ %04ds ] Dataset initialized' % (time.time() - start_time))
    interaction_matrix, interaction_weight = dataset.build_interactions(training_interactions)
    print('[ %04ds ] Interactions built' % (time.time() - start_time))

    no_components = 50
    loss = 'bpr'
    learning_rate = 0.1
    item_alpha = 5e-5
    user_alpha = 5e-5

    model = LightFM(no_components=no_components, loss=loss, learning_rate=learning_rate,
                    item_alpha=item_alpha, user_alpha=user_alpha)

    model.fit(interaction_matrix, sample_weight=interaction_weight, epochs=50, num_threads=4, verbose=True)
    print('[ %04ds ] Model fitted' % (time.time() - start_time))

    testing_set: List[Review] = Review.load_from_file(testing_set_file)
    print(len(testing_set))
    seen_testing_set = Review.extract_seen_reviews(testing_set, training_set)
    print(len(seen_testing_set))
    normalized_seen_testing_set = Review.normalize_by_user(seen_testing_set, user_avg)
    seen_pairs, ground_truth = Review.extract_sparse_testing_matrix_and_ground_truth(normalized_seen_testing_set)

    testing_interaction_matrix, testing_interaction_weight = dataset.build_interactions(seen_pairs)
    predictions = model.predict(testing_interaction_matrix.row, testing_interaction_matrix.col)
    # min_pred = np.min(predictions)
    # max_pred = np.max(predictions)
    # normalized_predictions = (np.array(predictions) - min_pred) / (max_pred - min_pred) * 4 + 1

    auc = roc_auc_score(np.array(ground_truth) >= 0, predictions)
    rmse = math.sqrt(mean_squared_error(ground_truth, predictions))

    print('[ %04ds ] Finished' % (time.time() - start_time))

    print("AUC = %.4f" % auc)
    print("RMSE = %.4f" % rmse)
