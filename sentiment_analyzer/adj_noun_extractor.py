import spacy


class AdjNounExtractor:
    def __init__(self):
        self.nlp = spacy.load('en')

    def extract(self, text):
        doc = self.nlp(text)

        adj_noun_pairs = []
        for token in doc:
            adjs = []
            nouns = []

            if token.pos_ in ('NOUN', 'PROPN'):
                for child in token.children:
                    if child.dep_ == 'amod':
                        adjs = self.get_conj(child)
                        nouns = self.get_conj(token)

            if token.pos_ == 'VERB':
                for child in token.children:
                    if child.dep_ == 'acomp':
                        adjs = self.get_conj(child)
                    if child.dep_ == 'nsubj':
                        nouns = self.get_conj(child)

            for adj in adjs:
                for noun in nouns:
                    adj_noun_pairs.append((adj, noun))

        return adj_noun_pairs

    def get_conj(self, token):
        conjs = [token]
        for child in token.children:
            if child.dep_ == 'conj':
                conjs.extend(self.get_conj(child))
        return conjs


if __name__ == '__main__':

    string_list = [
        "Great place to hang out after work: the prices are decent, and the ambience is fun. "
        "It's a bit loud, but very lively. The staff is friendly, and the food is good. "
        "They have a good selection of drinks.",
        "Both service and environment are good and great.",
        "It is an exciting and wonderful game, test, and experiment.",
        "The food tastes extremely good."
    ]

    extractor = AdjNounExtractor()
    for s in string_list:
        res = extractor.extract(s)
        print(s)
        print(res)
        print()
