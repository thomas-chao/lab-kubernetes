# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Redis Counter Demo in Docker
"""
import os
from flask import jsonify, json, abort, request
from . import app
from .models import Counter, DatabaseConnectionError

DEBUG = os.getenv("DEBUG", "False") == "True"
PORT = os.getenv("PORT", "5000")
DATABASE_URI = os.getenv("DATABASE_URI", "redis://:@localhost:6379/0")

counter = None

######################################################################
#   E R R O R   H A N D L E R S
######################################################################
@app.errorhandler(503)
def internal_server_error(error):
    """ Handles unexpected server error with 503_SERVICE_UNAVAILABLE """
    message = str(error)
    app.logger.error(message)
    return (
        jsonify(status=503, error="Service is unavailable", message=message),
        503,
    )

@app.errorhandler(400)
def internal_server_error(error):
    """ Handles bad requiest data """
    message = str(error)
    app.logger.error(message)
    return jsonify(status=400, error="Bad Request", message=message), 400


######################################################################
#   A P P L I C A T I O N   R O U T E S
######################################################################

# GET /
@app.route("/")
def index():
    """ Home Page """
    return app.send_static_file("index.html")


# GET /counter
@app.route("/counter", methods=["GET"])
def get_counter():
    """ get the counter """
    app.logger.info("Request to get counter")
    try:
        count = counter.value
    except Exception as err:
        abort(503, err)
    return jsonify(counter=count), 200


# POST /counter
@app.route("/counter", methods=["POST"])
def increment_counter():
    """ Increment the counter """
    app.logger.info("Request to increment counter")
    try:
        count = counter.increment()
    except Exception as err:
        abort(503, err)
    return jsonify(counter=count), 201


@app.route("/counter", methods=["PUT"])
def set_counter():
    """ Set the counter """
    app.logger.info("Request to set counter")
    try:
        data = request.get_json()
        if not data:
            abort(400, "Bad request data")
        new_count = int(data["counter"])
        app.logger.info("Setting counter to %s", new_count)
        counter.value = new_count
    except Exception as err:
        abort(503, err)
    return jsonify(counter=counter.value), 200


@app.route("/counter", methods=["DELETE"])
def delete_counter():
    """ Delete the counter """
    app.logger.info("Request to delete counter")
    try:
        del counter.value
    except Exception as err:
        abort(503, err)
    return "", 204


@app.before_first_request
def init_db():
    global counter
    try:
        app.logger.info("Initializing the Redis database")
        counter = Counter()
        counter.connect(DATABASE_URI)
        counter.value = 0
        app.logger.info('The Counter is now: %d', counter.value)
    except Exception as err:
        app.logger.error(str(err))
