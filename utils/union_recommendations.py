import json
import sys
import time


def load_recommendations(filename):
    user_recommendations = {}
    with open(filename, 'r') as f:
        raw_data = json.load(f)
        for row in raw_data['recommendations']:
            user_recommendations[row['user_id']] = set(row['recommended_businesses'])
    return user_recommendations


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python3 union_recommendations.py "
              "<PATH_TO_FIRST_RESULTS> <PATH_TO_SECOND RESULTS> <PATH_TO_OUTPUT_FILE>")
        exit(1)

    start_time = time.time()

    first_results_file = sys.argv[1]
    second_results_file = sys.argv[2]
    output_file = sys.argv[3]

    first_recommendations = load_recommendations(first_results_file)
    second_recommendations = load_recommendations(second_results_file)

    final_recommendations = []
    for user_id in first_recommendations.keys():
        final_recommendations.append({'user_id': user_id,
                                      'recommended_businesses': first_recommendations[user_id] |
                                                                second_recommendations[user_id]})

    with open(output_file, 'w') as f:
        json.dump({'recommendations': final_recommendations}, f, indent=4, separators=(', ', ': '))
