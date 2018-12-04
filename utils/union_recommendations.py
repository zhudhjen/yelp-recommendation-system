import sys
import time

if __name__ == '__main__':
    if len(sys.argv) != 6:
        print("Usage: python3 union_recommendations.py <PATH_TO_TRAINING_SET> "
              "<PATH_TO_TESTING_SET> <USER_STATS_FILE> <BUSINESS_STATS_FILE> <OUTPUT_FILE>")
        exit(1)

    start_time = time.time()

    training_set_file = sys.argv[1]
    testing_set_file = sys.argv[2]
    user_stats_file = sys.argv[3]
    business_stats_file = sys.argv[4]
    output_file = sys.argv[5]
