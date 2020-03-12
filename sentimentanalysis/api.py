import json
from typing import Union

from flask import Flask, request, Response
from werkzeug.exceptions import HTTPException, InternalServerError

from sentimentanalysis.analizer import SentimentAnalysis


def get_response(body: Union[str, dict], status: int = 200, message_as_json: bool=False):
    json_body = {("result" if status == 200 else "error"): body}

    return Response(json.dumps(json_body), status, mimetype="application/json")


app = Flask(__name__)
sent_analysis = SentimentAnalysis()


@app.errorhandler(Exception)
def handle_exception(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now you're handling non-HTTP exceptions only
    return get_response(f"500. HTTP Exception. Exception: {e}", 500)


@app.errorhandler(InternalServerError)
def handle_500(e):
    original = getattr(e, "original_exception", None)

    if original is None:
        return get_response("500. Unhandled Internal Server Error", 500)

    # wrapped unhandled error
    return get_response(f"500. Handled Internal Server Error: {original}", 500)


@app.route("/sentimentanalysis", methods=["POST"])
def get_sentiment_analysis():
    if not request.is_json:
        message = "Incorrect mimetype, must be 'application/json'."
        status_code = 415
    else:
        request_body = request.get_json()
        if "text" not in request_body:
            message = "'text' attribute not present in request body"
            status_code = 422
        else:
            text = request_body["text"]
            status_code = 200
            message = sent_analysis.compute_sentiment(text)

    return get_response(message, status_code, message_as_json=True)


@app.route("/")
def root():
    return "Everything is working fine"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
