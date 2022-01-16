from .application import app

def keep_alive():
    app.run(host="0.0.0.0", port=5000)
