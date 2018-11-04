import sys
import json
from adj_noun_extractor import AdjNounExtractor


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print('Please provide the path to the input file.')

    input_file = sys.argv[1]

    extractor = AdjNounExtractor()

    nouns_count = dict()
    with open(input_file, 'r') as f:
        for line in f:
            review = json.loads(line)
            pairs = extractor.extract(review['text'], lemma=True)
            for p in pairs:
                if p[1] in nouns_count:
                    nouns_count[p[1]] += 1
                else:
                    nouns_count[p[1]] = 1

    output_file = 'nouns_count.txt'
    with open(output_file, 'w') as f:
        for noun, count in nouns_count.items():
            f.write(noun + ' ' + str(count) + '\n')
