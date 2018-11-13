import sys

if __name__ == '__main__':

    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print('Usage: python nouns_filter.py [input_file] [output_file] [threshold=1000]')
        sys.exit(-1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    threshold = int(sys.argv[3]) if len(sys.argv) == 4 else 1000

    size = 0
    nouns = []
    with open(input_file, 'r') as f:
        for line in f:
            size += 1
            noun, count = line.split('  ')
            count = int(count)

            if count >= threshold and noun != '-PRON-':
                nouns.append(noun)

    with open(output_file, 'w') as f:
        for noun in nouns:
            f.write(noun + '\n')

    print("The number of nouns before filtering:", str(size))
    print("The number of nouns after filtering:", str(len(nouns)))
