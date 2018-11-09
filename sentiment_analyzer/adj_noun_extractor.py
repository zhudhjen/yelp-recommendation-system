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
            adv = None

            if token.pos_ in ('NOUN', 'PROPN'):
                for child in token.children:
                    if child.dep_ == 'amod':
                        adjs = self.get_conj(child)
                        nouns = self.get_conj(token)
                    if child.dep_ == 'neg':
                        adv = child.text

                if token.dep_ == 'attr':
                    for ancestor in token.ancestors:
                        if ancestor.pos_ == 'VERB':
                            for child in ancestor.children:
                                if child.dep_ == 'neg':
                                    adv = child.text

            if token.pos_ == 'VERB':
                for child in token.children:
                    if child.dep_ == 'acomp':
                        adjs = self.get_conj(child)
                    if child.dep_ == 'nsubj':
                        nouns = self.get_conj(child)
                    if child.dep_ == 'neg':
                        adv = child.text

            for adj in adjs:
                for noun in nouns:
                    lefts = [left.text for left in adj.lefts if left.pos_ == 'ADV']
                    if lefts:
                        adv = " ".join(lefts)

                    if adv is not None:
                        adj_noun_pairs.append((adv + ' ' + adj.text, noun.text, noun.lemma_))
                    else:
                        adj_noun_pairs.append((adj.text, noun.text, noun.lemma_))

        return adj_noun_pairs

    def get_conj(self, token):
        conjs = [token]
        for child in token.children:
            if child.dep_ == 'conj':
                conjs.extend(self.get_conj(child))
        return conjs


if __name__ == '__main__':

    sentences = [
        # adj and noun combinations
        "Both service and environment are good and great.",
        "It is an exciting and wonderful game, test, and experiment.",

        # adv
        "The food tastes extremely good. I think the movie is wonderfully awful.",
        "The food tastes extremely not bad. The food is not bad.",
        "It is not a bad thing. It is not bad.",

        # Real world examples
        "Great place to hang out after work: the prices are decent, and the ambience is fun.",
        "It's a bit loud, but very lively. The staff is friendly, and the food is good.",
        "They have a good selection of drinks.",
        "Fish and pork are awesome too. Service is above and beyond. Not a bad thing to say about this place."
    ]

    results = [
        # adj and noun combinations
        [('good', 'service', 'service'), ('good', 'environment', 'environment'), ('great', 'service', 'service'),
         ('great', 'environment', 'environment')],
        [('exciting', 'game', 'game'), ('exciting', 'test', 'test'), ('exciting', 'experiment', 'experiment'),
         ('wonderful', 'game', 'game'), ('wonderful', 'test', 'test'), ('wonderful', 'experiment', 'experiment')],

        # adv
        [('extremely good', 'food', 'food'), ('wonderfully awful', 'movie', 'movie')],
        [('extremely not bad', 'food', 'food'), ('not bad', 'food', 'food')],
        [('not bad', 'thing', 'thing'), ('not bad', 'It', '-PRON-')],

        # Real world examples
        [('Great', 'place', 'place'), ('decent', 'prices', 'price'), ('fun', 'ambience', 'ambience')],
        [('loud', 'It', '-PRON-'), ('friendly', 'staff', 'staff'), ('good', 'food', 'food')],
        [('good', 'selection', 'selection')],
        [('awesome', 'Fish', 'fish'), ('awesome', 'pork', 'pork'), ('Not bad', 'thing', 'thing')]
    ]

    extractor = AdjNounExtractor()
    for s, r in zip(sentences, results):
        res = extractor.extract(s)
        print("True" if res == r else "False")
        # print(s)
        # print(res)
        # print()
