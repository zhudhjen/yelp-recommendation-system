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
        print("Usage: python3 lightfm_with_features_recommendation.py <PATH_TO_TRAINING_SET> "
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

    all_user_ids = User.extract_user_ids(user_stats)
    all_business_ids = Business.extract_business_ids(business_stats)

    dataset = Dataset()
    dataset.fit(all_user_ids, all_business_ids,
                user_features=all_user_features, item_features=all_business_features)

    user_features = dataset.build_user_features(
        User.build_user_features(user_stats, all_user_ids), True)

    business_features = dataset.build_item_features(
        Business.build_business_features(business_stats, all_business_ids), True)

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
    # n_users = len(training_user_ids)
    best_k = 50
    user_id_map, _, business_id_map, __ = dataset.mapping()

    business_ids_list = list(training_business_ids)
    training_business_indices = np.array(list(map(lambda id: business_id_map[id], business_ids_list)))
    user_seen_businesses = Review.extract_user_seen_business(training_set)

    print('[ %04ds ] Ready to produce recommendations' % (time.time() - start_time))
    finished = 0
    with open('user_list.json', 'r') as f:
        recommendation_user_list = json.load(f)['users']

    n_users = len(recommendation_user_list)
    for user_id in recommendation_user_list:
        # user_recommendations = {'user_id': user_id, 'recommended_businesses': []}
        user_index = user_id_map[user_id]
        predictions = model.predict(np.repeat(user_index, n_businesses), training_business_indices)
        recommendations_list = np.array(business_ids_list)[np.argsort(-np.array(predictions))[:best_k]]
        # predictions_with_bid = list(zip(predictions, business_ids_list))
        # sorted_predictions = sorted(predictions_with_bid, reverse=True)
        # for prediction, bid in sorted_predictions:
        #     if bid not in user_seen_businesses[user_id]:
        #         user_recommendations['recommended_businesses'].append(bid)
        #     if len(user_recommendations['recommended_businesses']) >= best_k:
        #         break
        recommendations.append({'user_id': user_id, 'recommended_businesses': recommendations_list.tolist()})
        finished += 1
        if finished % 100 == 0:
            print('[ %04ds ] Finished recommendations: %08d/%08d' % (time.time() - start_time, finished, n_users))
        if finished % (n_users / 100) == 0:
            print('[ %04ds ] Finished recommendations: %02d%%' % (time.time() - start_time, finished / (n_users / 100)))
        if finished > 100000:
            break

    with open(output_file, 'w') as f:
        json.dump({'recommendations': recommendations}, f, indent=4, separators=(', ', ': '))
