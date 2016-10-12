from flask import Flask, render_template
from flask_ask import Ask, statement, question, session


import logging
from random import randint
import time
import threading

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from baseConfig import config

app = Flask(__name__)
ask = Ask(app, '/')
logging.getLogger('flask_ask').setLevel(logging.DEBUG)


scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name(config['FILENAME'], scope)
gc = gspread.authorize(credentials)

NUM_FACTS = 0
FACT_LIST = []

# Get latest from google spreadsheet on the start of every game
def _get_latest_facts():
    # Probably cleaner way to do this
    global FACT_LIST
    global NUM_FACTS
    sht = gc.open_by_key(config['SPREADSHEET_KEY'])
    worksheet = sht.get_worksheet(0)
    facts = worksheet.col_values(1)
    # gspread returns '', hence filter
    FACT_LIST = filter(None, facts)
    NUM_FACTS = len(FACT_LIST)
    return

_get_latest_facts()


@ask.launch
def new_game():
    _get_latest_facts()
    return say_fact()

@ask.intent('GetNewFactIntent')
def say_fact():
    print 'got here'
    fact_index = randint(0, NUM_FACTS-1)
    fact = FACT_LIST[fact_index]
    return question(fact)

@ask.intent('LastFactIntent')
def last_fact():
    fact_index = NUM_FACTS-1
    fact = FACT_LIST[fact_index]
    return statement(fact)

@ask.intent('AMAZON.StopIntent')
def stop():
    bye_text = render_template('bye')
    return statement(bye_text)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
