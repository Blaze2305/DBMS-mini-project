from flask import Flask
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

app.secret_key = 'SECRETKEY123123#'

from app.route import mainRoutes,userRoutes
from app import utils
