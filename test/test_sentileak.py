import os

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


def test_custom_base_url_not_found():
    with pytest.raises(FileNotFoundError):
        _ = SentiLeak(custom_base_url="data2")


def test_custom_base_url():
    _ = SentiLeak(custom_base_url=f"./sentileak/data")
