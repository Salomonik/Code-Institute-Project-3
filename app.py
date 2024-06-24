import os
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

CLIENT_ID = os.environ.get('TWITCH_CLIENT_ID')
CLIENT_SECRET = os.environ.get('TWITCH_CLIENT_SECRET')