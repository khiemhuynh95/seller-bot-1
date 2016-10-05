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
					try:
						sender_id = messaging_event["sender"]["id"]		# the facebook ID of the person sending you the message
						recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
						payload = messaging_event["postback"]["payload"]  # the payload text
						onPostbackEvent(sender_id, recipient_id, payload)
					except:
						pass

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
	if payload == "FEATURE":
		doMoreFeature(sender_id)
	if payload == "LOCATION":
		showLocation(sender_id)
	if payload == "VIDEO":
		showVideo(sender_id)

def showTShirtProducts(recipient_id):
	elements = [{
					"title": "Nice Blue T-Shirt - $19.99",
					"item_url": "http://www.lazada.vn/ao-thun-nam-co-tru-xanh-navi-2035572.html",
					"image_url": "http://vn-live-02.slatic.net/p/ao-thun-nam-co-tru-xanh-co-vit-1405-3755302-0a0daa09d238345d6a267ba403f7abbe-catalog_233.jpg",
					"buttons":[
			             {
				            "type":"web_url",
				            "url":"http://www.lazada.vn/ao-thun-nam-co-tru-xanh-navi-2035572.html",
				            "title":"Show now"
			             },
			             {
			             	"type": "postback",
			             	"title":"More feature",
			             	"payload" : "FEATURE"
			             }
			        ]
				},
				{	
					"title": "Light Green T-Shirt - $21.99",
					"item_url": "http://zanado.com/ao-thun-nam-jackies-b202-dep-gia-re-sid48907.html?color=98",
					"image_url": "http://a4vn.com/media/catalog/product/cache/all/thumbnail/255x298/7b8fef0172c2eb72dd8fd366c999954c/1/3/13_40_2.jpg",
					"buttons":[
			             {
				            "type":"web_url",
				            "url":"http://zanado.com/ao-thun-nam-jackies-b202-dep-gia-re-sid48907.html?color=98",
				            "title":"Show now"
			             }
			        ]
				},
				{	
					"title": "Raglan T-Shirt red & white- $12.99",
					"item_url": "http://www.lazada.vn/ao-thun-nam-tay-raglan-do-do-phoi-trang-2056856.html?mp=1",
					"image_url": "http://vn-live-01.slatic.net/p/ao-thun-nam-tay-raglan-do-do-phoi-trang-2581-6586502-2d977472b068b70467eeb4e9d2e1122d-catalog_233.jpg",
					"buttons":[
			             {
				            "type":"web_url",
				            "url":"http://www.lazada.vn/ao-thun-nam-tay-raglan-do-do-phoi-trang-2056856.html?mp=1",
				            "title":"Show now"
			             }
			        ]
				}]
				
	doGenericTemplate(recipient_id, elements)

def showLocation(recipient_id):
	latitude = 10.762952
	longitude = 106.682340
	
	elements = [	
					{
                    'title': "Nova Shop",
                    'subtitle': "Nguyen Van Cu, D5, HCM city",
                    #'image_url': 'http://staticmap.openstreetmap.de/staticmap.php?center=' + latitude + ',' + longitude + '&zoom=18&size=640x480&markers=' + latitude + ',' + longitude + ',ol-marker',
                    #'image_url' : 'http://staticmap.openstreetmap.de/staticmap.php?center=10.762952,106.682340&zoom=15&size=640x480&markers=10.762952,106.682340,ol-marker',
                    'buttons': [{
                        'type': 'web_url',
                        #'url': 'http://staticmap.openstreetmap.de/staticmap.php?center=' + latitude + ',' + longitude + '&zoom=18&size=640x480&markers=' + latitude + ',' + longitude + ',ol-marker',
                        'url': 'http://maps.google.com/maps?q=loc:' + latitude + ',' + longitude + '&z=20',
                        'title': "Show directions"
                    	}
                	]
                	}
                ]
	doGenericTemplate(recipient_id,elements)

def showVideo(recipient_id):
	data = json.dumps({
		  "recipient":{
		    "id":recipient_id
		  },
		  "message":{
		    "attachment":{
		      "type":"video",
		      "payload":{
		        "url":"https://video-ams3-1.xx.fbcdn.net/v/t42.1790-2/14598671_198279837271500_3673022822852067328_n.mp4?efg=eyJybHIiOjQxOSwicmxhIjo4MjAsInZlbmNvZGVfdGFnIjoidjNfNDI2X2NyZl8yM19tYWluXzMuMF9zZCJ9&rl=419&vabr=233&oh=3ca3715476e9c768264061d2cdbdbe43&oe=57F4E8BA"
		      }
		    }
		  }
		})
	postData(data)

#Show more feature: videos and location
def doMoreFeature(recipient_id):
	data = json.dumps({
	"recipient":{
	    "id":recipient_id
	  },
	  "message":{
	    "attachment":{
	      "type":"template",
	      "payload":{
	        "template_type":"button",
	        "text":"What do you want to do next?",
	        "buttons":[
	          {
	            "type":"postback",
	            "title":"Products on Video",
	            "payload": "VIDEO"
	          },
	          {
	            "type":"postback",
	            "title":"Shop location",
	            "payload":"LOCATION"
	          },
	          {
	            "type":"postback",
	            "title":"Show webiste",
	            "payload":"WEBSITE"
	          }
	        ]
	      }
	    }
	  }
	})
	postData(data)

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
	data = json.dumps({
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
		})
	
	log("doGenericTemplate--------------")
	log(data)

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