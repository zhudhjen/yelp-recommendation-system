import sys

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print('Please provide path to the input file and the output file.')
        sys.exit(-1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    threshold = int(sys.argv[3]) if len(sys.argv) >= 4 else 2

    size = 0
    nouns_count = []
    with open(input_file, 'r') as f:
        for line in f:
            size += 1
            noun, count = line.split(' ')
            count = int(count)

            if count >= threshold:
                nouns_count.append((noun, count))

    nouns_count.sort(key=lambda x: x[1], reverse=True)

    with open(output_file, 'w') as f:
        for noun, _ in nouns_count:
            f.write(noun + '\n')

    print("Before filtering:", str(size))
    print("After filtering:", str(len(nouns_count)))
