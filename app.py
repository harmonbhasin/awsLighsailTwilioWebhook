from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import gspread
from Google import Create_Service
from datetime import date
import calendar

app = Flask(__name__)

@app.route('/sms', methods = ['POST'])
def	sms():
	# Get the message from the user sent to our Twilio number
	body = request.values.get('Body', None)

	# Start our TwiML response	
	resp = MessagingResponse()

	# Import account
	sa = gspread.service_account(filename = "service_account.json")

	# Get list of clients arrays
	client_list = ["Prototype"]
	for client in client_list:
		sh = sa.open(client)
	wks = sh.worksheet("Schedule")
	scraped_list = wks.get("A2:B8")

	# Determine the right reply for this message
	curr_date = date.today()
	workout_day=calendar.day_name[curr_date.weekday()]

	try:
		daily_schedule={day[0]:day[1] for day in scraped_list}
		for day in daily_schedule:
			if day==workout_day:
				if daily_schedule[day].lower() == body.lower():
					resp.message('Carpe Diem!')
				elif body.lower() == "no" and daily_schedule[day].lower()=="yes":
					resp.message("Stop lying bruh, excuses and excuses")
				elif body.lower() == "yes" and daily_schedule[day].lower()=="no":
					resp.message("Take a rest day bud")
	except:
		resp.message("Fill out the spreadsheet")
		
	return str(resp)

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port = 5000)
