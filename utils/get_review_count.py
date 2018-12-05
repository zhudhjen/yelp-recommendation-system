import sys
import json

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print('Usage: python get_review_count.py [input_file] [output_file]')
        sys.exit(-1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    businesses = []
    with open(input_file, 'r') as f:
        for line in f:
            obj = json.loads(line)
            business = dict()
            business['business_id'] = obj['business_id']
            business['review_count'] = obj['review_count']
            businesses.append(business)

    with open(output_file, 'w') as f:
        for business in businesses:
            f.write(json.dumps(business))
            f.write('\n')
