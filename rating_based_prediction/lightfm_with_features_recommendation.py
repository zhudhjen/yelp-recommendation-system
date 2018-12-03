import json
import sys
import time
from typing import List, Dict

import numpy as np
from lightfm import LightFM
from lightfm.data import Dataset

from utils.models import Review, User, Business

if __name__ == '__main__':
    if len(sys.argv) != 6:
        print("Usage: python3 lightfm_experiment.py <PATH_TO_TRAINING_SET> "
              "<PATH_TO_TESTING_SET> <USER_STATS_FILE> <BUSINESS_STATS_FILE> <OUTPUT_FILE>")
        exit(1)

    start_time = time.time()

    training_set_file = sys.argv[1]
    testing_set_file = sys.argv[2]
    user_stats_file = sys.argv[3]
    business_stats_file = sys.argv[4]
    output_file = sys.argv[5]

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
    training_user_ids = Review.extract_user_ids(normalized_training_reviews)
    training_business_ids = Review.extract_business_ids(normalized_training_reviews)

    interaction_matrix, interaction_weight = dataset.build_interactions(training_interactions)

    print('[ %04ds ] Interactions built' % (time.time() - start_time))

    no_components = 50
    loss = 'bpr'
    learning_rate = 0.1
    item_alpha = 1e-5
    user_alpha = 1e-5
    epochs = 50

    model = LightFM(no_components=no_components, loss=loss, learning_rate=learning_rate,
                    item_alpha=item_alpha, user_alpha=user_alpha)

    model.fit(interaction_matrix, sample_weight=interaction_weight, epochs=epochs, num_threads=4, verbose=True)
    print('[ %04ds ] Model fitted' % (time.time() - start_time))

    recommendations = []
    n_businesses = len(training_business_ids)
    n_users = len(training_user_ids)
    best_k = 100
    user_id_map, business_id_map = dataset.mapping()
    user_seen_businesses = Review.extract_user_seen_business(training_set)
    for user in range(n_users):
        user_recommendations = {'user_id': user_id_map[user], 'recommended_businesses': []}
        predictions = model.predict(np.repeat(user, n_businesses), np.arange(0, n_businesses))
        predictions_with_bid = list(zip(predictions, np.arange(0, n_businesses)))
        sorted_predictions = sorted(predictions_with_bid, reverse=True)
        for prediction, bid in sorted_predictions:
            if business_id_map[bid] not in user_seen_businesses[user_id_map[user]]:
                user_recommendations['recommended_businesses'].append(bid)

    with open(output_file, 'w') as f:
        json.dump(recommendations, f)
