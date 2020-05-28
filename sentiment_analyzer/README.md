# Sentiment Analyzer

Some usages and details about sentiment analyzer.

## Usages

Run Python files below in order:
1. ../data_partitioner/sequence_partition.py (**optional**)
2. extract_triples.py
3. nouns_counter.py
4. nouns_filter.py
5. find_relevant_nouns.ipynb
6. calculate_sentiment_polarity.py
7. aggregate_sentiment_polarity.py
8. compute_aspect_score.py
9. rating.py

## Details

* adj_noun_extractor.py
    * A Python class that can extract adjective-noun pairs from review text
* spark_vs_loop.ipynb
    * Time comparison between Spark and loop with `AdjNounExtractor`
* extract_triples.py
    * Extract (adverb adjective, noun, base format of noun) triples from review text
* nouns_counter.py
    * Count base format of nouns in adjective-noun pairs extracted from review text
* nouns_filter.py
    * Use a threshold to remove nouns appearing less than certain times
* find_relevant_nouns.ipynb
    * Convert words to GloVe vectors
    * View words in 2D plot
    * Find relevant nouns given some aspects
* calculate_sentiment_polarity.py
    * Calculate sentiment polarity for every adjective-noun pairs
* aggregate_sentiment_polarity.py
    * Aggregate reviews with same business ID
* compute_aspect_score.py
    * Compute average score of every aspect for every business
* rating.py
    * Scale sentiment polarity (-1.0 to 1.0) to rating (0 to 5)
