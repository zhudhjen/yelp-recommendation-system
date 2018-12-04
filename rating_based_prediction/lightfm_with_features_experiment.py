import math
import sys
import time
from typing import List, Dict

import numpy as np
from lightfm import LightFM
from lightfm.data import Dataset
from sklearn.metrics import mean_squared_error, roc_auc_score

from utils.models import Review, User, Business

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: python3 lightfm_with_features_experiment.py <PATH_TO_TRAINING_SET> "
              "<PATH_TO_TESTING_SET> <USER_STATS_FILE> <BUSINESS_STATS_FILE>")
        exit(1)

    start_time = time.time()

    training_set_file = sys.argv[1]
    testing_set_file = sys.argv[2]
    user_stats_file = sys.argv[3]
    business_stats_file = sys.argv[4]

    print('[ %04ds ] Program started' % (time.time() - start_time))

    training_set: List[Review] = Review.load_from_file(training_set_file)
    user_stats: Dict[str, User] = User.load_from_file(user_stats_file)
    business_stats: Dict[str, Business] = Business.load_from_file(business_stats_file)

    print('[ %04ds ] Files loaded' % (time.time() - start_time))

    all_user_features = ['NO_FEAT']
    all_business_features = Business.collect_business_features(business_stats)

    dataset = Dataset()
    dataset.fit(User.extract_user_ids(user_stats),
                Business.extract_business_ids(business_stats),
                user_features=all_user_features, item_features=all_business_features)

    user_features = dataset.build_user_features(
        User.build_user_features(user_stats, User.extract_user_ids(user_stats)), True)

    business_features = dataset.build_item_features(
        Business.build_business_features(business_stats, Business.extract_business_ids(business_stats)), True)

    print('[ %04ds ] Dataset initialized' % (time.time() - start_time))

    user_avg, user_std = Review.extract_user_average_and_std(training_set)
    normalized_training_reviews = Review.normalize_by_user(training_set, user_avg)
    training_interactions = Review.extract_sparse_interaction_matrix(normalized_training_reviews)

    interaction_matrix, interaction_weight = dataset.build_interactions(training_interactions)

    print('[ %04ds ] Interactions built' % (time.time() - start_time))

    no_components = 50
    loss = 'bpr'
    learning_rate = 0.1
    item_alpha = 1e-5
    user_alpha = 1e-5
    epochs = 20

    model = LightFM(no_components=no_components, loss=loss, learning_rate=learning_rate,
                    item_alpha=item_alpha, user_alpha=user_alpha)

    model.fit(interaction_matrix, sample_weight=interaction_weight, epochs=epochs, num_threads=4, verbose=True)
    print('[ %04ds ] Model fitted' % (time.time() - start_time))

    testing_set: List[Review] = Review.load_from_file(testing_set_file)
    seen_testing_set, unseen_testing_set = Review.extract_seen_reviews(testing_set, training_set)
    print(len(seen_testing_set), len(unseen_testing_set))
    normalized_seen_testing_set = Review.normalize_by_user(seen_testing_set, user_avg)
    seen_pairs, ground_truth = Review.extract_sparse_testing_matrix_and_ground_truth(normalized_seen_testing_set)

    testing_interaction_matrix, _ = dataset.build_interactions(seen_pairs)
    predictions = model.predict(testing_interaction_matrix.row, testing_interaction_matrix.col)

    # min_pred = np.min(predictions)
    # max_pred = np.max(predictions)
    # normalized_predictions = (np.array(predictions) - min_pred) / (max_pred - min_pred) * 4 + 1

    user_test_map = {}
    for seen_pair, gt in zip(seen_pairs, ground_truth):
        user, business = seen_pair
        if user not in user_test_map:
            user_test_map[user] = [], []
        user_test_map[user][0].append(seen_pair)
        user_test_map[user][1].append(gt)

    # user_auc = []
    # not_defined_users = 0
    # for _, user_entry in user_test_map.items():
    #     pairs, user_gt = user_entry
    #     if np.count_nonzero(np.array(user_gt) >= 0) == 0 or np.count_nonzero(np.array(user_gt) >= 0) == len(user_gt):
    #         not_defined_users += 1
    #         continue
    #     user_testing_interaction_matrix, user_testing_interaction_weight = dataset.build_interactions(pairs)
    #     user_predictions = model.predict(user_testing_interaction_matrix.row, user_testing_interaction_matrix.col)
    #     user_auc.append(roc_auc_score(np.array(user_gt) >= 0, user_predictions))

    # print(len(user_auc), not_defined_users)

    auc = roc_auc_score(np.array(ground_truth) >= 0, predictions)
    # uauc = np.mean(user_auc)
    rmse = math.sqrt(mean_squared_error(ground_truth, predictions))

    print('[ %04ds ] Finished' % (time.time() - start_time))

    print("AUC = %.4f" % auc)
    # print("UAUC = %.4f" % uauc)
    print("RMSE = %.4f" % rmse)
