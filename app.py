from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from db import Base, Item
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "Airbnb"


# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# TODO: Add auth
# Add json api

@app.route('/')
def index():
    pass


@app.route('/')
def create():
    pass


@app.route('/')
def read():
    pass


@app.route('/')
def edit():
    pass


@app.route('/')
def delete():
    pass


@app.route('/')
def login():
    pass


if __name__ == '__main__':
    app.secret_key = 'uB6YxmvEGccMqabK'
    app.debug = True
    app.run(host='0.0.0.0')
