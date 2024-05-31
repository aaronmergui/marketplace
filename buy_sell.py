from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

import json
from database import db
from models import User

buy_sell = Blueprint('buy_sell', __name__)
market_place_address = '0x15f2D312937032F79F70c14D1d8A88b695097c89'

