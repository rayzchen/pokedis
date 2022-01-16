from flask import Flask
from .library import AfterResponse
from .blueprint import bp

app = Flask(__name__)

with app.app_context():
    app.register_blueprint(bp, url_prefix="/")
    AfterResponse(app)
