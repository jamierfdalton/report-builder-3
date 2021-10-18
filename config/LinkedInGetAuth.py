import requests
from urllib.parse import urlparse
import urllib
import time, json
import functions

with open ("./encrypted_files/linkedinsecrets.json") as file:
	secrets = json.loads(file)

def main():
	responseType = 'code'
	clientId = secrets["clientId"]
	redirectUri = secrets["redirectUri"]
	state = secrets["state"]
	scope = secrets["scope"]

	authenticationRequest = 'https://www.linkedin.com/oauth/v2/authorization?response_type='+ responseType + '&client_id=' + clientId + '&redirect_uri=' +  redirectUri + '&state=' + state + '&scope=' + scope

	return authenticationRequest

def access_exchange(authCode):

	accessTokenUrl = 'https://www.linkedin.com/oauth/v2/accessToken'
	clientId = secrets["clientId"]
	redirectUri = secrets["redirectUri"]
	clientSecret = secrets["clientSecret"]

	payload = { 'grant_type': 'authorization_code',
				'code': authCode,
				'redirect_uri': redirectUri,
				'client_id': clientId,
				'client_secret': clientSecret}

	response = requests.post(accessTokenUrl, data=payload)
	response = response.json()

	print(response)

	access_token = response['access_token']
	print ("Access Token:", access_token)
	print ("Expires in (seconds):", response['expires_in'])

	functions.writeToFile(access_token, './encrypted_files/linkedin_access_token.txt', 'w+')
