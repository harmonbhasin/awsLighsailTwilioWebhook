import gspread
import calendar
import requests
import pandas as pd
import re
import time
import csv
import random
import os
import MySQLdb
import openai

from dotenv import load_dotenv
from Google import Create_Service
from Helper import process_csv, flatten
from datetime import date
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from waitress import serve

#from flask_ngrok import run_with_ngrok # TESTING ONLY

app = Flask(__name__)

#run_with_ngrok(app) # TESTING ONLY

load_dotenv()

@app.route('/sms', methods = ['POST'])
def	sms():

  # Get the message from the user sent to our Twilio number
  body = request.values.get('Body', None)
  number = request.values.get('From', None)

  # Import openai key
  openai.api_key = os.getenv("OPENAI_API_KEY")

  print(number)

  # Establish connection with database
  connection = MySQLdb.connect(
    host     = os.getenv("HOST"),
    user     = os.getenv("USERNAME"),
    passwd   = os.getenv("PASSWORD"),
    db       = os.getenv("DATABASE"),
    ssl      = {
    "ca": "./cert.pem",
    }
  )

  # Create a cursor object to execute queries
  cursor = connection.cursor()

  # Define the query
  query = """ SELECT pr.programName
          FROM Personal p
          INNER JOIN Client c ON p.id = c.personalId
          INNER JOIN Profile pr ON c.profileId = pr.id
          WHERE p.phone = %s
          """

  # Execute the query
  cursor.execute(query, (number,))

  # Fetch 
  client = cursor.fetchone()
  print(client)

  # Close the cursor and connection
  cursor.close()
  connection.close()
  
  # Start our TwiML response	
  resp = MessagingResponse()

  # Import account
  sa = gspread.service_account(filename = "service_account.json")

  data=process_csv("quotes.csv")

  new_data=flatten(data)
  quote_list=list()

  for quote in new_data:
    if ";success" in quote and quote[0].isupper()==True:
        quote_list.append(quote.split(";success")[0])
    if ";motivational" in quote and quote[0].isupper()==True:
        quote_list.append(quote.split(";motivational")[0])

  quote_df=pd.read_csv("quotes.csv")
  quote_map={}

  for i in range(len(quote_df)):
    quote_map[quote_df["Author"].iloc[i]]=quote_df["Quote"].iloc[i]
  person=random.choice(list(quote_map.keys()))

  sh=sa.open(client[0])

  if re.search("[0-9]{2,3}", body):
    diet=sh.worksheet("BodyProgress")
    values_list = diet.col_values(1)[1:]

    if len(values_list)==56:
      diet.batch_clear(["A2:A57"])
      diet.update("A2:A57", float(body))
    else:
      diet.update(("A"+str(len(values_list)+2)), float(body))

    resp.message('Are you working out today (Yes or No)?')

  else:   
    curr_date = date.today()
    workout_day=calendar.day_name[curr_date.weekday()]
    wks=sh.worksheet("Schedule")
    list_of_lists = wks.get_all_values()
    list_of_lists[1:]
    daily_schedule={day[0]:day[1] for day in list_of_lists[1:]}

    client_msg = body.lower()
    schedule = daily_schedule[workout_day]

    class Response:
      day = daily_schedule[workout_day]
      yes = "yes"
      no = "no"
      assist = "help"

    match client_msg:
      case Response.day:
        resp.message(quote_map[person] + " - " + person)

      case Response.yes:
        resp.message("Take a rest day bud")

      case Response.no:
        resp.message("Stop lying bruh, excuses and excuses")

      case _:
        result = openai.Completion.create(
          model="text-davinci-003",
          prompt=body,
          max_tokens=128,
          temperature=0.5
          )
        resp.message(result.choices[0].text) 

  return str(resp)

if __name__ == '__main__':
	serve(app, host = '0.0.0.0', port = 5000)
	#app.run() TESTING ONLY
