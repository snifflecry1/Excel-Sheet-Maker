from flask import Blueprint
from . import views

urls = Blueprint('main', __name__)

urls.add_url_rule('/hello', view_func=views.hello)
urls.add_url_rule('/create_spreadsheet', view_func=views.create_spreadsheet)
