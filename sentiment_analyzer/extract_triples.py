import sys
import json
import time

from pyspark import SparkContext, SparkConf
from adj_noun_extractor import AdjNounExtractor


def extract(line):
    obj = json.loads(line)
    text = obj['text']
    triples = extractor.extract(text)
    obj['triples'] = triples
    return [json.dumps(obj)]


if __name__ == '__main__':

    # Read input file path and output file path
    if len(sys.argv) != 3:
        print('Usage: python extract_triples.py [input_file] [output_file]')
        sys.exit(-1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Initial Spark
    conf = SparkConf() \
        .setAppName('spaCy') \
        .setMaster('local[*]') \
        .set('spark.executor.memory', '8G') \
        .set('spark.driver.memory', '4G') \
        .set('spark.driver.maxResultSize', '4G')
    sc = SparkContext(conf=conf)

    # Initial extractor
    extractor = AdjNounExtractor()

    # Start timing
    start = time.time()

    # Read data and convert them to rdd
    with open(input_file, 'r') as f:
        lines = f.readlines()
    rdd = sc.parallelize(lines, numSlices=1000)

    # Extract
    results = rdd.map(extract).reduce(lambda x, y: x + y)

    # End timing
    end = time.time()
    print(end - start)

    # Output
    with open(output_file, 'w') as f:
        for line in results:
            f.write(line + '\n')
