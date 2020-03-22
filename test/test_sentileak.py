import pytest

from sentileak import SentiLeak


@pytest.fixture(scope="session")
def sent_analyzer():
    sent_analyzer = SentiLeak()
    return sent_analyzer


def test_empty_text(sent_analyzer):
    result = sent_analyzer.compute_sentiment("")
    assert (
        result["global_sentiment"] == 0.0 and len(result["per_sentence_sentiment"]) == 0
    )


def test_not_empty_text(sent_analyzer):
    result = sent_analyzer.compute_sentiment("Texto con una frase")
    assert len(result["per_sentence_sentiment"]) > 0
