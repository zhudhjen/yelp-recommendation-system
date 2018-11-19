import sys
import json
import time


def compute_scores(reviews):
    # aspect: [polarity, count]
    scores = {key: [0.0, 0] for key in relevant_nouns_to_aspect.values()}

    for review in reviews:
        for quadruple in review['relevant_quadruples']:
            aspect = relevant_nouns_to_aspect[quadruple[2]]
            polarity = quadruple[3]
            scores[aspect][0] += polarity
            scores[aspect][1] += 1

    # Compute mean score for every aspect
    for key, value in scores.items():
        mean = value[0] / value[1] if value[1] != 0 else 0.0
        value.insert(0, mean)

    return scores


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print('Usage: python compute_aspect_score.py [input_file] [output_file]')
        sys.exit(-1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Read relevant nouns into a dictionary
    relevant_nouns_file = 'data/relevant_nouns_to_aspect.json'
    with open(relevant_nouns_file, 'r') as f:
        relevant_nouns_to_aspect = json.load(f)

    # Start timing
    start = time.time()

    # Compute aspect score for every business
    businesses = []
    with open(input_file, 'r') as f:
        for line in f:
            obj = json.loads(line)
            businesses.append({
                'business_id': obj['business_id'],
                'scores': compute_scores(obj['reviews'])
            })

    # End timing
    end = time.time()
    print('Computation time:', end - start)

    # Start timing
    start = time.time()

    # Output
    with open(output_file, 'w') as f:
        for business in businesses:
            f.write(json.dumps(business))
            f.write('\n')

    # End timing
    end = time.time()
    print('Output time:', end - start)
