from flask import Flask, redirect, request, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import os
import config_builder
import json, yaml
import encrypter
import requests

app = Flask(__name__)
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
	with open("./encrypted_files/users.json") as json_file:
		users = json.load(json_file)
	if username in users and check_password_hash(users.get(username),password):
		return username

@app.route('/')
@auth.login_required
def index():
	return redirect("/api/getconfig")

@app.route('/form')
def form():
	return "Form handled"

@app.route('/updategoogle', methods=['POST'])
def updateGoogle():
	newTokens = request.form

	auth = request.authorization
	username = auth.username
	password = auth.password

	oldFile = "/code/encrypted_files/google-ads.yaml"
	data = yaml.safe_load(oldFile)
	print("old version: ", flush=True)
	print(data, flush=True)

	data['access_token'] = newTokens['access_token']
	try:
		data['refresh_token'] = newTokens['refresh_token']
	except:
		pass

	print("new version: ", flush=True)
	print(data, flush=True)

	os.remove(oldFile)
	with open("/code/encrypted_files/google-ads.yaml2" ,"w+") as file:
		file.write(yaml.dump(data))

	# encrypter.encryptFile("/code/encrypted_files/google-ads.yaml", username, password)

	return 0

@app.route('/api/getconfig')
### @auth.login_required was removed from here as it now resides in frontend app.py. 
def getconfig():
	output = config_builder.buildConfig()
	return output

if __name__ == '__main__':
	if os.environ.get('PORT') is not None:
		app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT'))
	else:
		app.run(debug=True, host='0.0.0.0')
