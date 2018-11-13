import sys
import json
import os


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print('Usage: python nouns_counter.py [input_directory] [output_file]')
        sys.exit(-1)
    input_dir = sys.argv[1]
    output_file = sys.argv[2]

    # Only use files ending with 'triples.json' in the input directory
    files = os.listdir(input_dir)
    files = [file for file in files if file.endswith('triples.json')]

    # Count nouns with their base format
    nouns_count = dict()
    for file in files:
        with open(os.path.join(input_dir, file), 'r') as f:
            for line in f:
                triples = json.loads(line)['triples']
                for triple in triples:
                    if triple[2] in nouns_count:
                        nouns_count[triple[2]] += 1
                    else:
                        nouns_count[triple[2]] = 1

    # Sort nouns by their count in descending order
    results = sorted(nouns_count.items(), key=lambda x: x[1], reverse=True)

    # Output
    with open(output_file, 'w') as f:
        for noun, count in results:
            f.write(noun + '  ' + str(count) + '\n')
