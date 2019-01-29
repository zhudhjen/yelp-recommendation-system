import json
from adj_noun_extractor import AdjNounExtractor
from textblob import TextBlob


class SentimentAnalyzer:
    def __init__(self):
        self.extractor = AdjNounExtractor()
        with open('data/relevant_nouns_to_aspect.json', 'r') as f:
            self.nouns_to_aspect = json.load(f)

    def analyze(self, review, print_flag=False):
        triples = self.extractor.extract(review)
        relevant_triples = [triple for triple in triples if triple[2] in self.nouns_to_aspect]
        res = []
        for triple in relevant_triples:
            text = ' '.join([triple[0], triple[1]])
            polarity = TextBlob(text).sentiment.polarity
            res.append((triple[0], triple[1], self.nouns_to_aspect[triple[2]], polarity))

        if print_flag:
            print(triples)
            print(relevant_triples)
        return res
