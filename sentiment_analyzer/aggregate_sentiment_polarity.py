import sys
import json
import os
import time


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print('Usage: python aggregate_sentiment_polarity.py [input_directory] [output_file]')
        sys.exit(-1)
    input_dir = sys.argv[1]
    output_file = sys.argv[2]

    # Only use files ending with 'quadruples.json' in the input directory
    files = os.listdir(input_dir)
    files = [file for file in files if file.endswith('quadruples.json')]

    # Start timing
    start = time.time()

    # Aggregate reviews with same business
    business_to_review = dict()
    for file in files:
        with open(os.path.join(input_dir, file), 'r') as f:
            for line in f:
                review = json.loads(line)
                obj = dict()
                obj['review_id'] = review['review_id']
                obj['relevant_quadruples'] = review['relevant_quadruples']

                if review['business_id'] not in business_to_review:
                    business_to_review[review['business_id']] = []
                business_to_review[review['business_id']].append(obj)

    # End timing
    end = time.time()
    print('Aggregation time:', end - start)

    # Start timing
    start = time.time()

    # Output
    with open(output_file, 'w') as f:
        for key, value in business_to_review.items():
            obj = dict()
            obj['business_id'] = key
            obj['reviews'] = value
            f.write(json.dumps(obj))
            f.write('\n')

    # End timing
    end = time.time()
    print('Output time:', end - start)
