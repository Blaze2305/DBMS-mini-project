from flask import request,jsonify,Response
from app import app

@app.route("/")
def initRoute():
    return  "HELLO WORLD"