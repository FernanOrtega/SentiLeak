from typing import Dict

import snowballstemmer
import spacy

from spacy.tokens.doc import Doc
from spacy.tokens.span import Span
from spacy.tokens.token import Token
from itertools import groupby

from sentimentanalysis.dataloader import load_dict


class SentimentAnalysis(object):
    def __init__(self, language="es"):
        self.__nlp = spacy.load("es_core_news_md")
        stemmer = StemmerPipe(language)
        annotator = SentimentAnnotatorPipe(language)

        self.__nlp.add_pipe(stemmer)
        self.__nlp.add_pipe(annotator)

    def compute_sentiment(self, text: str, language="es") -> Dict:
        result = {}
        doc = self.__nlp(text)

        result["per_sentence_sentiment"] = self.__compute_per_sentence_sentiment(doc)
        result["global_sentiment"] = self.__compute_global_sentiment(doc)

        return result

    def __compute_per_sentence_sentiment(self, doc: Doc) -> Dict:

        result = {}

        for i, sent in enumerate(doc.sents):
            max_score = 0.0
            min_score = 0.0

            for token in sent:
                score = token._.sentiment_weight * token._.negation_weight
                if score > 0:
                    score = max(1.0, score + token._.booster_weight)
                    if score > max_score:
                        max_score = max
                elif score < 0:
                    score = min(-1.0, score - token._.booster_weight)
                    if score < min_score:
                        min_score = score

            sentence_score = max_score + min_score
            sent._.sentiment_weight = sentence_score
            result[i] = sentence_score

        return result

    def __compute_global_sentiment(self, doc: Doc) -> float:

        max_score = 0.0
        min_score = 0.0

        for sent in doc.sents:
            if sent._.sentiment_weight > max_score:
                max_score = sent._.sentiment_weight
            elif sent._.sentiment_weight < min_score:
                min_score = sent._.sentiment_weight

        return max_score + min_score


class SentimentAnnotatorPipe(object):
    def __init__(self, language: str = "es"):
        self.__sentiment_words = load_dict(language, "sentiment_words.csv")
        self.__boosters = load_dict(language, "boosters.csv")
        self.__negations = load_dict(language, "negations.csv")
        Span.set_extension("sentiment_weight", default=0.0, force=True)
        Token.set_extension("sentiment_weight", default=0.0, force=True)
        Token.set_extension("negation_weight", default=1.0, force=True)
        Token.set_extension("booster_weight", default=0.0, force=True)

    def __call__(self, doc: Doc) -> Doc:
        self.__annotate_sentiment_words(doc)
        self.__annotate_negations_and_boosters(doc)

        return doc

    def __annotate_sentiment_words(self, doc: Doc) -> None:
        for token in doc:
            if token.pos_ == "ADJ" and not token.is_stop:
                sentiment_weight = self.__sentiment_words.get(token._.stem, 0.0)
                if sentiment_weight != 0.0:
                    token._.booster_weight = self.__get_self_boosters(token)
                    token._.sentiment_weight = sentiment_weight

    def __annotate_negations_and_boosters(self, doc: Doc) -> None:
        for sentence in doc.sents:
            for i, token in enumerate(sentence):
                if token in self.__negations:
                    influenced_token = self.__get_influenced_token(sentence, i)
                    if influenced_token:
                        influenced_token._.negation_weight = (
                            self.__negations.get(token) * -1
                        )
                elif token in self.__boosters:
                    influenced_token = self.__get_influenced_token(sentence, i)
                    if influenced_token:
                        influenced_token._.booster_weight += self.__boosters.get(token)

    def __get_influenced_token(self, sentence: Span, influencer_index: int) -> Token:

        result = None
        for i in range(1, len(sentence)):
            for j in [-1, 1]:
                candidate_index = influencer_index + i * j
                if 0 <= candidate_index < len(sentence):
                    candidate = sentence[candidate_index]

                    if candidate._.sentiment_weight != 0.0:
                        result = candidate
                        break

        return result

    def __get_self_boosters(self, token: Token) -> float:

        return (
            1.0
            if (token.shape_.count("X") / len(token)) > 0.8
            or self.__max_rep_letters(token) >= 3
            else 0.0
        )

    def __max_rep_letters(self, token: Token) -> int:

        return sorted(
            [(letter, len(list(group))) for letter, group in groupby(token.lower_)],
            key=lambda i: i[1],
            reverse=True,
        )[0][1]


class StemmerPipe(object):
    def __init__(self, language="es"):
        self.__stemmer = snowballstemmer.stemmer("spanish")
        Token.set_extension("stem", default="")

    def __call__(self, doc: Doc) -> Doc:
        for token in doc:
            token._.stem = self.__stemmer.stemWord(token.lemma_)

        return doc
