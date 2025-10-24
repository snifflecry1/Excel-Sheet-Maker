from flask import render_template

def hello():
    return 'Hello, World!'

def create_spreadsheet(name: str) -> int:
    return 0