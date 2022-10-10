from typing import Dict

import snowballstemmer
import spacy

from spacy.tokens.doc import Doc
from spacy.tokens.span import Span
from spacy.tokens.token import Token
from itertools import groupby

from .dataloader import load_dict

from spacy.cli import download


def load_spacy_model(model_name):
    """
    Method to load SpaCy models. If the model isn't available, it will download it.
    :param model_name: the name of the SpaCy model
    :return: the loaded model
    """
    try:
        nlp = spacy.load(model_name)
    except OSError:
        print(f"Model {model_name} wasn't found. Downloading now...")
        download(model_name)
        nlp = spacy.load(model_name)

    return nlp


class SentiLeak(object):
    """
    SentiLeak class. This is the main class to compute sentiment analysis. It has a strong dependency with
    Spacy package since it uses it to text processing.
    """

    def __init__(self, language="es", custom_base_url: str = None):
        """
        Init method
        :param language: input language
        """
        self.__nlp = load_spacy_model("es_core_news_sm")
        stemmer = StemmerPipe(language)
        annotator = SentimentAnnotatorPipe(language, custom_base_url=custom_base_url)

        self.__nlp.add_pipe(stemmer)
        self.__nlp.add_pipe(annotator)

    def compute_sentiment(self, text: str, language="es") -> Dict:
        """
        Method to compute sentiment of an input text. Default language is Spanish.
        :param text: input text
        :param language: language of input text
        :return: a dictionary that contains both global sentiment and sentence-level sentiment
        """
        result = {}
        doc = self.__nlp(text)

        result["per_sentence_sentiment"] = self.__compute_per_sentence_sentiment(doc)
        result["global_sentiment"] = self.__compute_global_sentiment(doc)

        return result

    def __compute_per_sentence_sentiment(self, doc: Doc) -> []:
        """
        Internal method to compute sentence-level sentiment.
        :param doc: SpaCy document
        :return: dictionary with sentence-level sentiment
        """

        result = []

        for i, sent in enumerate(doc.sents):
            max_score = 0.0
            min_score = 0.0

            for token in sent:
                score = token._.sentiment_weight * token._.negation_weight
                if score > 0:
                    score = max(1.0, score + token._.booster_weight)
                    if score > max_score:
                        max_score = score
                elif score < 0:
                    score = min(-1.0, score - token._.booster_weight)
                    if score < min_score:
                        min_score = score

            sentence_score = max_score + min_score
            sent._.sentiment_weight = sentence_score
            dict_sent_result = {
                "position": i,
                "text": str(sent),
                "score": sentence_score,
            }
            result.append(dict_sent_result)

        return result

    def __compute_global_sentiment(self, doc: Doc) -> float:
        """
        Internal method to compute global sentiment
        :param doc: SpaCy document
        :return: the global sentiment
        """

        max_score = 0.0
        min_score = 0.0

        for sent in doc.sents:
            if sent._.sentiment_weight > max_score:
                max_score = sent._.sentiment_weight
            elif sent._.sentiment_weight < min_score:
                min_score = sent._.sentiment_weight

        return max_score + min_score


class SentimentAnnotatorPipe(object):
    """
    This class is defined as a SpaCy pipe, that is, it is integrated into the SpaCy's pipeline.

    It produces, at token-level, all the required annotations to computer both global and sentence-level sentiment.
    """

    def __init__(self, language: str = "es", custom_base_url: str = None):
        """
        Init method
        :param language: language of the annotation
        """
        if custom_base_url:
            self.__sentiment_words = load_dict(language, "sentiment_words.csv", base_url=custom_base_url)
            self.__boosters = load_dict(language, "boosters.csv", base_url=custom_base_url)
            self.__negations = load_dict(language, "negations.csv", base_url=custom_base_url)
        else:
            self.__sentiment_words = load_dict(language, "sentiment_words.csv")
            self.__boosters = load_dict(language, "boosters.csv")
            self.__negations = load_dict(language, "negations.csv")
        Span.set_extension("sentiment_weight", default=0.0, force=True)
        Token.set_extension("sentiment_weight", default=0.0, force=True)
        Token.set_extension("negation_weight", default=1.0, force=True)
        Token.set_extension("booster_weight", default=0.0, force=True)

    def __call__(self, doc: Doc) -> Doc:
        """
        Method that is called when executing the pipeline
        :param doc: SpaCy document
        :return: SpaCy document
        """
        self.__annotate_sentiment_words(doc)
        self.__annotate_negations_and_boosters(doc)

        return doc

    def __annotate_sentiment_words(self, doc: Doc) -> None:
        """
        Method to annotate sentiment words
        :param doc: SpaCy document
        :return:
        """
        for token in doc:
            # if token.pos_ == "ADJ": -> It seems that this filter doesn't work well
            sentiment_weight = self.__sentiment_words.get(token._.stem, 0.0)
            if sentiment_weight != 0.0:
                token._.booster_weight = self.__get_self_boosters(token)
                token._.sentiment_weight = sentiment_weight

    def __annotate_negations_and_boosters(self, doc: Doc) -> None:
        """
        Method to annotate negations and boosters
        :param doc: SpaCy document
        :return:
        """
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
        """
        Method to discover the token that is influenced by the one located in @influencer_index index.
        :param sentence: Span that represents the sentence
        :param influencer_index: index in which the influencer token is located
        :return: the influenced token
        """

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
        """
        Method to compute whether the token contains self-boosters or not
        :param token: SpaCy token
        :return: value of self-booster
        """

        return (
            1.0
            if (token.shape_.count("X") / len(token)) > 0.8
               or self.__max_rep_letters(token) >= 3
            else 0.0
        )

    def __max_rep_letters(self, token: Token) -> int:
        """
        Method to compute the maximum number of repeated letters in a given token. It tries to detect situations like:
        'Helloooooooo'
        :param token: SpaCy token
        :return: the maximum number of repeated letters in input token
        """

        return sorted(
            [(letter, len(list(group))) for letter, group in groupby(token.lower_)],
            key=lambda i: i[1],
            reverse=True,
        )[0][1]


class StemmerPipe(object):
    """
    This class is defined as a SpaCy pipe, that is, it is integrated into the SpaCy's pipeline.

    It produces, at token-level, the stem version of the token.
    """

    def __init__(self, language="es"):
        """
        Init method
        :param language: input language
        """
        self.__stemmer = snowballstemmer.stemmer("spanish")
        Token.set_extension("stem", default="", force=True)

    def __call__(self, doc: Doc) -> Doc:
        """
        Method that is called when executing the pipeline
        :param doc: SpaCy document
        :return: SpaCy document
        """
        for token in doc:
            token._.stem = self.__stemmer.stemWord(token.lemma_)

        return doc
