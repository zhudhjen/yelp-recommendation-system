import sys
import os


if __name__ == '__main__':

    if len(sys.argv) != 4:
        print('Usage: python sequence_partition.py [input_file] [output_directory] [num_of_partition]')
        sys.exit(-1)
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    num_of_partition = int(sys.argv[3])

    # If output directory does not exist, create one
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # Read data into memory line by line and split them to different lists
    files = [[] for _ in range(num_of_partition)]
    with open(input_file, 'r') as f:
        for i, line in enumerate(f):
            files[i % num_of_partition].append(line)

    # Output
    name, ext = os.path.basename(input_file).split('.')
    for i, file in enumerate(files):
        filename = output_dir + '/' + name + '_' + str(i+1) + '.' + ext
        with open(filename, 'w') as f:
            for line in file:
                f.write(line)
