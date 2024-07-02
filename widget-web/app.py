import os
import logging
# from google.auth.transport import requests
# from google.oauth2 import id_token
from flask import Flask, request, render_template, session, abort, redirect

WIDGET_ID = os.getenv('WIDGET_ID')
EXPECTED_AUDIENCE= os.getenv('EXPECTED_AUDIENCE')

app = Flask(__name__)
app.secret_key = "ai-help-desk"

@app.route("/")
def index():
    # user_info=session["user_info"]
    # if not user_info:
    #     abort(401, description='Unauthorized: Missing IAP JWT')
    # print(user_info)
    user_info = {
        "widget_id": WIDGET_ID
    }
    return render_template("index.html", user_info=user_info)

@app.route("/help")
def help():
    return render_template("help.html")

if __name__ == "__main__":
    # When running locally with Flask's development server this disables
    # OAuthlib's HTTPs verification. When running in production with a WSGI
    # server such as gunicorn this option will not be set and your application
    # *must* use HTTPS.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    app.run("localhost", 8080, debug=True)

# @app.before_request
# async def validateIapHeader(req):
#     """
#     Validates the IAP JWT in the request header.

#     Args:
#         req: The incoming request object.
#     """

#     iap_jwt = req.headers.get('X-Goog-IAP-JWT-Assertion')
#     if not iap_jwt:
#         abort(401, description='Unauthorized: Missing IAP JWT')

#     if not EXPECTED_AUDIENCE:
#         abort(500, description="EXPECTED_AUDIENCE is not set")

#     try:
#         # Verify the JWT
#         id_info = id_token.verify_oauth2_token(
#             iap_jwt,
#             requests.Request(),
#             EXPECTED_AUDIENCE
#         )

#         # Extract user information
#         session["credentials"] = {
#                 "token": iap_jwt,
#                 "user_id": id_info.get('sub'),
#                 "user_email": id_info.get('email')
#             }
#     except ValueError as e:
#         abort(401, description=str(e))

