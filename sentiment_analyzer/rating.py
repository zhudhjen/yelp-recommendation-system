import sys
import json


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print('Usage: python rating.py [input_file] [output_file]')
        sys.exit(-1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Scaling factors
    aspects = {'Food', 'Service', 'Costs', 'Environment', 'Location'}
    min_scores = {aspect: 1.0 for aspect in aspects}
    max_scores = {aspect: -1.0 for aspect in aspects}

    # Flatten
    total_count = 0
    NA_count = 0
    businesses = []
    with open(input_file, 'r') as f:
        for line in f:
            total_count += 5
            business = json.loads(line)
            for key, value in business['scores'].items():
                if value[2] == 0:
                    business[key] = 'N/A'
                    NA_count += 1
                else:
                    min_scores[key] = min(min_scores[key], value[0])
                    max_scores[key] = max(max_scores[key], value[0])
                    business[key] = value[0]
            del business['scores']
            businesses.append(business)

    # Scaling
    diff = {aspect: max_scores[aspect] - min_scores[aspect] for aspect in aspects}
    for business in businesses:
        for key, value in business.items():
            if key == 'business_id' or value == 'N/A':
                continue

            # Scale to 0-5
            business[key] = (value - min_scores[key]) / diff[key] * 5
            business[key] = round(business[key], 2)

    # Statistics
    print('Total aspects:', total_count)
    print('Valid aspects:', total_count - NA_count)

    # Output
    with open(output_file, 'w') as f:
        for business in businesses:
            f.write(json.dumps(business))
            f.write('\n')
