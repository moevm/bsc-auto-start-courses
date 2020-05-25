from flask import Flask

app = Flask(__name__)
# app.config.from_object('config')
from app import routes
from app import google_api
from app import github_api
from app import moodle_api

