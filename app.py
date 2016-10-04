import os
import sys
import json

import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
	# when the endpoint is registered as a webhook, it must echo back
	# the 'hub.challenge' value it receives in the query arguments
	if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
		if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
			return "Verification token mismatch", 403
		return request.args["hub.challenge"], 200

	return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

	# endpoint for processing incoming messaging events

	data = request.get_json()
	log(data)  # you may not want to log every incoming message in production, but it's good for testing

	if data["object"] == "page":

		for entry in data["entry"]:
			for messaging_event in entry["messaging"]:

				if messaging_event.get("message"):  # someone sent us a message
					sender_id = messaging_event["sender"]["id"]		# the facebook ID of the person sending you the message
					recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
					message_text = messaging_event["message"]["text"]  # the message's text

					onMessageEvent(sender_id, recipient_id, message_text)

				if messaging_event.get("delivery"):  # delivery confirmation
					pass

				if messaging_event.get("optin"):  # optin confirmation
					pass

				if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
					sender_id = messaging_event["sender"]["id"]		# the facebook ID of the person sending you the message
					recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
					payload = messaging_event["postback"]["payload"]  # the payload text
					onPostbackEvent(sender_id, recipient_id, payload)

	return "ok", 200

def postData(data):
	params = {
		"access_token": os.environ["PAGE_ACCESS_TOKEN"]
	}
	headers = {
		"Content-Type": "application/json"
	}

	r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
	if r.status_code != 200:
		log(r.status_code)
		log(r.text)

def onPostbackEvent(sender_id, recipient_id, payload):
	if payload == "T_SHIRT":
		showTShirtProducts(sender_id)

def showTShirtProducts(recipient_id):
	# products = [
	#	 {
	#		 title: 
	#	 }
	# ]

	elements = [
				{
					"title":"Welcome to Peter\'s Hats",
					"item_url":"https://petersfancybrownhats.com",
					"image_url":"https://petersfancybrownhats.com/company_image.png",
					"subtitle":"We\'ve got the right hat for everyone.",
					"buttons": [
						{
							"type":"payment",
							"title":"buy",
							"payload":"DEVELOPER_DEFINED_PAYLOAD",
							"payment_summary":{
							"currency":"USD",
							"payment_type":"FIXED_AMOUNT",
							"merchant_name":"Peter's Apparel",
							"requested_user_info":[
								"shipping_address",
								"contact_name",
								"contact_phone",
								"contact_email"
							],
							"price_list":[
								{
								"label":"Subtotal",
								"amount":"29.99"
								},
								{
								"label":"Taxes",
								"amount":"2.47"
								}
							]
							}
						}
					]
				}
				]
	doGenericTemplate(recipient_id, elements)

def onMessageEvent(sender_id, recipient_id, message_text):
	doSenderActions(sender_id)
	if message_text == "hello":
		greeting(sender_id)

def greeting(sender_id):
	text = "Welcome to Nova shop, what are you looking for today?"
	buttons = [
				  {
					"type":"postback",
					"title":"T-Shirt",
					"payload":"T_SHIRT"
				  },
				  {
					"type":"postback",
					"title":"Jean",
					"payload":"JEAN"
				  },
				  {
					"type":"postback",
					"title":"Wallet",
					"payload":"WALLET"
				  }
				]
	doButtonTemplate(sender_id, text, buttons)

# Generic Template
def doGenericTemplate(recipient_id, elements):
	data = {
		"recipient":{
			"id":recipient_id
		},
		"message":{
			"attachment":{
			"type":"template",
			"payload":{
				"template_type":"generic",
				"elements":elements
			}
			}
		}
		}
	
	postData(data)


# Button Template
def doButtonTemplate(recipient_id, text, buttons):
	data = json.dumps({
		  "recipient":{
			"id":recipient_id
		  },
		  "message":{
			"attachment":{
			  "type":"template",
			  "payload":{
				"template_type":"button",
				"text":text,
				"buttons": buttons
			  }
			}
		  }
		})

	postData(data)

# Sender Actions
def doSenderActions(recipient_id):
	data = json.dumps({
	  "recipient":{
	  	"id":recipient_id
	  },
	  "sender_action":"typing_on"
	})
	postData(data)

# Text Message
def doTextMessage(recipient_id, message_text):
	#log("doTextMessage to {recipient}: {text}".format(recipient=recipient_id, text=message_text))
	data = json.dumps({
		"recipient": {
			"id": recipient_id
		},
		"message": {
			"text": message_text
		}
	})
	postData(data)

 # simple wrapper for logging to stdout on heroku
def log(message): 
	print str(message)
	sys.stdout.flush()


if __name__ == '__main__':
	app.run(debug=True)