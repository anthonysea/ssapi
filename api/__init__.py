from flask import Flask
import config
from . import *

app = Flask(__name__)
app.config.from_object('config')




