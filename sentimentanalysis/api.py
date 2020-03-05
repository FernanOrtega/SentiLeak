import json
from flask import Flask, request, Response
from werkzeug.exceptions import HTTPException, InternalServerError


def get_response(body, status=200):
    json_body = {
        ("value" if status == 200 else "error"): body
    }

    return Response(json.dumps(json_body), status, mimetype='application/json')


def handle_method_not_allowed():
    message = "The method is not allowed for the requested URL."
    status_code = 405

    return get_response(message, status_code)


app = Flask(__name__)


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
        message = "Ok"
        status_code = 200

    return get_response(message, status=status_code)


@app.route("/")
def root():
    return "Everything is working fine"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
