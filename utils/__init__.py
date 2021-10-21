from .database import db
from .helper import *

for server in db["servers"]:
    db["servers"][server]["battling"] = []