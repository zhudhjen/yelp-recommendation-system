import errno
import os
import random
import sys


def sample(reviews: list, ratio: float):
    total = len(reviews)
    print('Sampling %f from %d items' % (ratio, total))

    n = total
    n_sample = int(n * ratio)
    samples = []
    for review in reviews:
        if n % (total / 10) == 0:
            print('Finished: %d0%%' % (11 - n / (total / 10)))
        if random.randint(1, n) <= n_sample:
            samples.append(review)
            n -= 1
            n_sample -= 1
        else:
            n -= 1
    print('Done\n')

    return samples


def partition_three_sets(reviews: list, ratio_1: float, ratio_2: float):
    total = len(reviews)
    print('Sampling (%f, %f, %f) from %d items' % (ratio_1, ratio_2, 1 - ratio_1 - ratio_2, total))

    n = total
    n_1 = int(n * ratio_1)
    n_2 = int(n * (ratio_1 + ratio_2))

    set_1 = []
    set_2 = []
    set_3 = []
    for review in reviews:
        if n % (total / 10) == 0:
            print('Finished: %d0%%' % (11 - n / (total / 10)))

        rnd = random.randint(1, n)
        if rnd > n_2:
            set_3.append(review)
            n -= 1
        elif rnd > n_1:
            set_2.append(review)
            n -= 1
            n_2 -= 1
        else:
            set_1.append(review)
            n -= 1
            n_1 -= 1
            n_2 -= 1

    print('Done\n')
    return set_1, set_2, set_3


def write_set(reviews: list, path: str):
    print('Writing %d items to "%s"' % (len(reviews), path))
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(path, 'w', encoding='UTF-8') as output_file:
        output_file.writelines(reviews)

    print('Done\n')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 partition.py [input_review_file] [output_directory]")
        exit(1)
    input_file_name = sys.argv[1]
    output_dir = sys.argv[2]

    dev_ratio = 0.3

    training_ratio = 0.8
    validation_ratio = 0.1
    testing_ratio = 0.1

    with open(input_file_name, 'r', encoding='UTF-8') as input_file:
        all_reviews = input_file.readlines()

    print('Reading done\n')

    training_set, validation_set, testing_set = partition_three_sets(all_reviews, training_ratio, validation_ratio)

    write_set(training_set, output_dir + '/full_partitions/reviews_training_set.json')
    write_set(validation_set, output_dir + '/full_partitions/reviews_validation_set.json')
    write_set(testing_set, output_dir + '/full_partitions/reviews_testing_set.json')

    dev_reviews = sample(all_reviews, dev_ratio)
    del all_reviews

    write_set(dev_reviews, output_dir + '/reviews_dev.json')

    dev_training_set, dev_validation_set, dev_testing_set = partition_three_sets(dev_reviews, training_ratio,
                                                                                 validation_ratio)

    write_set(dev_training_set, output_dir + '/dev_partitions/reviews_training_set.json')
    write_set(dev_validation_set, output_dir + '/dev_partitions/reviews_validation_set.json')
    write_set(dev_testing_set, output_dir + '/dev_partitions/reviews_testing_set.json')
