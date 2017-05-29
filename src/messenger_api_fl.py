import json
import os
import requests
from flask import Flask
from flask import request
from flask import make_response
from flask import abort
from sys import argv
import apiai

# Messenger API parameters
FB_VERIFY_TOKEN = os.environ.get('FB_VERIFY_TOKEN')
# A user secret to verify webhook get request.
FB_PAGE_TOKEN = os.environ.get('FB_PAGE_TOKEN')
#APIAI client access token
APIAI_ACCESS_TOKEN = os.environ.get('APIAI_ACCESS_TOKEN')

# Flask app should start in global layout
app = Flask(__name__)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
	if request.method == 'GET':
		'''
		Returns the challenge during first verification.
		'''
		verify_token = request.args.get('hub.verify_token')
		# check whether the verify tokens match
		if verify_token == FB_VERIFY_TOKEN:
			# respond with the challenge to confirm
			challenge = request.args.get('hub.challenge')
			return challenge
		else:
			return 'Invalid Request or Verification Token'

	elif request.method == 'POST':
		req = request.get_json(silent=True, force=True)
		print req,type(req)
		if req['object'] == 'page':
				for entry in req['entry']:
					messages = entry['messaging']
					if messages[0]:
						# Get the first message
						message = messages[0]
                		
                		# Retrieve the Facebook user ID of the sender
						fb_id = message['sender']['id']

						if message.has_key('message'):
							# Retrive text from message
							text = message['message']['text']

							#Send request to api.ai agent.
							req = ai_client.text_request()
							req.query = text

							#Get Response from api.ai agent.
							reply = req.getresponse()
							#Conversation can be maintained in log.
							reply = json.loads(reply.read())
							print reply
							
							#Forward response to messenger.	
							fb_message(fb_id, reply['result']['fulfillment']['speech'])
		
		return 'Completed'

	else:
		abort(400)

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
	data = {
		'recipient': {'id': sender_id},
		'message': {'text': text}
	}
    
	resp = postData(data)
	
	return resp.content

ai_client = apiai.ApiAI(APIAI_ACCESS_TOKEN)

if __name__ == '__main__':
	app.run(debug=False, port=argv[1], host='0.0.0.0')