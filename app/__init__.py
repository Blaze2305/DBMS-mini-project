from flask import Flask

app = Flask(__name__)

app.secret_key = 'SECRETKEY123123#'

from app.route import mainRoutes,userRoutes
from app import utils
