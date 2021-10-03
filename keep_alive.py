import flask
import os

app = flask.Flask(__name__)

@app.route("/")
def index():
    return "Bot is online"

@app.route("/hook")
def hook():
    os.system("git pull")
    open("restart", "w+").close()
    return flask.Response(status=200)

@app.route("/restart")
def restart():
    open("restart", "w+").close()
    return flask.redirect("/")

@app.route("/stop")
def stop():
    open("stop", "w+").close()
    return flask.redirect("/")

def keep_alive():
    app.run()
