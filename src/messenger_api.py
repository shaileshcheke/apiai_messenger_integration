#!/usr/bin/env python
#Messenger api.ai integration example.

from bottle import Bottle, request, debug
import requests
import os
from sys import argv
import json
import apiai

# Messenger API parameters
FB_VERIFY_TOKEN = os.environ.get('FB_VERIFY_TOKEN')
# A user secret to verify webhook get request.
FB_PAGE_TOKEN = os.environ.get('FB_PAGE_TOKEN')
#APIAI client access token
APIAI_ACCESS_TOKEN = os.environ.get('APIAI_ACCESS_TOKEN')

#Setup a bottle server.
debug(True)
app = Bottle()

@app.get('/webhook')
def messenger_webhook():
	"""
	A webhook to return a challenge
	"""
	verify_token = request.query.get('hub.verify_token')
	# check whether the verify tokens match
	if verify_token == FB_VERIFY_TOKEN:
		# respond with the challenge to confirm
		challenge = request.query.get('hub.challenge')
		return challenge
	else:
		return 'Invalid Request or Verification Token'

# Facebook Messenger POST Webhook
@app.post('/webhook')
def messenger_post():
	data = request.json
	print data
	if data['object'] == 'page':
		for entry in data['entry']:
			messages = entry['messaging']
			if messages[0]:
				# Get the first message
				message = messages[0]
                # Yay! We got a new message!
                # We retrieve the Facebook user ID of the sender
				fb_id = message['sender']['id']
				if message.has_key('message'):
					text = message['message']['text']

					req = ai_client.text_request()
					req.query = text
					reply = req.getresponse()
					#Conversation can be maintained in log.

					reply = json.loads(reply.read())
					print reply
					
					fb_message(fb_id, reply['result']['fulfillment']['speech'])
		
		return 'Completed'
	else:
		return 'Received Different Event'
	return None

#Utility functions

#Send POST request to messenger
def postData(data):
	"""
	Function to execute post operation.
	"""
	# Setup the query string with your PAGE TOKEN
	qs = 'access_token=' + FB_PAGE_TOKEN
	# Send POST request to messenger
	resp = requests.post('https://graph.facebook.com/me/messages?' + qs,
                         json=data)
	return resp

def fb_message(sender_id, text):
	"""
	Function for returning response to messenger
	"""
	print text
	data = {
		'recipient': {'id': sender_id},
		'message': {'text': text}
	}
    
	resp = postData(data)
	return resp.content

ai_client = apiai.ApiAI(APIAI_ACCESS_TOKEN)

if __name__ == '__main__':
	#Add persistent menu to chat interface
	# Run Server
	app.run(host='0.0.0.0', port=argv[1])