import flask
import os
from utils import api

app = flask.Flask("__main__")
app.register_blueprint(api.bp)

@app.route("/")
def index():
    return "Bot is online"

@app.route("/hook", methods=["POST", "GET"])
def hook():
    os.system("git pull")
    open("restart", "w+").close()
    return flask.Response(status=200)

@app.route("/db")
def db():
    with open("db.json") as f:
        resp = app.response_class(
            response=f.read(),
            status=200,
            mimetype="application/json"
        )
        return resp

# @app.route("/restart")
# def restart():
#     open("restart", "w+").close()
#     return flask.redirect("/")

# @app.route("/stop")
# def stop():
#     open("stop", "w+").close()
#     return flask.redirect("/")

def keep_alive():
    app.run(host="0.0.0.0", port=5000)
