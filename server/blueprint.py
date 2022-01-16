import flask
import os

bp = flask.Blueprint("bp", __name__)

@bp.route("/")
def index():
    return "Bot is online"

@bp.route("/hook", methods=["POST", "GET"])
def hook():
    @flask.current_app.after_response
    def worker():
        os.system("git fetch")
        os.system("git reset --hard origin/main")
        open("restart", "w+").close()
    
    return flask.Response(status=200)

@bp.route("/db")
def db():
    with open("db.json") as f:
        resp = flask.current_app.response_class(
            response=f.read(),
            status=200,
            mimetype="application/json"
        )
        return resp

# @bp.route("/restart")
# def restart():
#     open("restart", "w+").close()
#     return flask.redirect("/")

# @bp.route("/stop")
# def stop():
#     open("stop", "w+").close()
#     return flask.redirect("/")
