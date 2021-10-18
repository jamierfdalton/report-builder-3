from flask import Flask, render_template, url_for, redirect, request, flash
from flask_httpauth import HTTPBasicAuth
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
import pyAesCrypt
import os
import requests
import json, yaml
import time
import functions
import updateauth

global config

### This is a temporary skeleton for implementing a real login system in future, so we're not worried about the
### Security implications of a plain-text password.
r = requests.get('http://config:5000/api/getconfig', auth=("flagship", "fl48h1p"))

config = json.loads(r.text)

f = open("config.json", "w")
f.write(r.text)
f.close()
f = open("config.json", "r")
f.close()

# This import happens late so that we have config.json saved for the db_functions login details
import db_functions as db

os.remove("config.json")

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
	with open("./encrypted_files/users.json") as json_file:
		users = json.load(json_file)
	if username in users and check_password_hash(users.get(username),password):
		return username

# Connection attempt counter.
attempts = 0

# Limiting the file-types that can be uploaded for the image upload sections to prevent malicious file uploads
UPLOAD_FOLDER = "./static/uploads/"
ALLOWED_EXTENSIONS = {'png', 'jpeg', 'jpg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Make sure that frontend isn't cached by the browser
app.config['SEND_FILE_MAX_AGE_DEFAULT']=120

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/output')
@auth.login_required
def output():

	r = requests.get('http://config:5000/api/getconfig')

	config = json.loads(r.text)

	f = open("config.json", "w")
	f.write(r.text)
	f.close()
	f = open("config.json", "r")
	f.close()

	functions.createFollowerGraphs("Country")
	functions.createFollowerGraphs("Industry")
	functions.createFollowerGraphs("Job Function")
	functions.createFollowerGraphs("Region")
	functions.createFollowerGraphs("Seniority")
	functions.createFollowerGraphs("Staff Count")

	# Output is the main dynamic page in frontend, using data from the config file and the database to create dynamic reports.
	pagetitle = str(config['companyIDs']['companyName'] + " Report for " + config['dateSettings']['todayddmmyy'] )
	title1="Campaign Performance - LinkedIn Organic"
	linkedInOrganicStats = db.getSumOfLinkedInOrganicStats(config['dateSettings']['todayddmmyy'])
	prevlinkedInOrganicStats = db.getSumOfLinkedInOrganicStats(config['dateSettings']['lastFortnightDateTimeddmmyyyy'])
	newFollowers = db.followerGain30Days()
	uniqueVisitors = db.uniqueVisitors(config['dateSettings']['timeDeltaDaysPastYYYYMMDD'])
	organicImpressions = functions.endAtWhiteSpace(db.findHighestResult("impressions", config['dateSettings']['todayddmmyy'], offset=2)[0][1], 20)+" ..."
	organicImpressionNo = str(db.findHighestResult("impressions", config['dateSettings']['todayddmmyy'], offset=2)[0][0])
	organicClicks = functions.endAtWhiteSpace(db.findHighestResult("clicks", config['dateSettings']['todayddmmyy'], offset=1)[0][1], 20)+" ..."
	organicClicksNo = str(db.findHighestResult("clicks", config['dateSettings']['todayddmmyy'], offset=1)[0][0])
	organicCtr = str(db.findHighestResult("CTR", config['dateSettings']['todayddmmyy'], offset=1)[0][1])[:125]+" ..."
	organicCtrNo = str(round(float(db.findHighestResult("CTR", config['dateSettings']['todayddmmyy'], offset=1)[0][0])*100,3))
	organicShares = functions.endAtWhiteSpace(db.findHighestResult("shares", config['dateSettings']['todayddmmyy'], offset=0)[0][1], 20)+" ..."
	organicSharesNo = str(db.findHighestResult("shares", config['dateSettings']['todayddmmyy'], offset=0)[0][0])
	title2 = "Campaign Demographics - LinkedIn Organic"
	title3 ="Recent Followers"
	title4 = "Campaign Performance - LinkedIn Sponsored"
	sponsored1 = functions.sumOfLinkedInStats(db.getSumOfLinkedInSponsoredStats(config['dateSettings']['todayddmmyy']))
	sponsored2 = functions.sumOfLinkedInStats(db.getSumOfLinkedInSponsoredStats(config['dateSettings']['lastFortnightDateTimeddmmyyyy']))
	campaigns = functions.displayCampaignStats(db.getSumOfLinkedInSponsoredStats(config['dateSettings']['todayddmmyy']))
	title5 = "Demographics - LinkedIn Sponsored Campaigns by Company"
	campaignDemos = db.getdemosbycompany(config['campaignIDs']['campaignURNs'])
	title6 = "Google Ads Campaigns"
	googleCampaignToDate = functions.displayGoogleCampaignStats(db.getGoogle_Data(config['dateSettings']['todayddmmyy']))


	return render_template('output.html',
		pagetitle=pagetitle,
		title1=title1,
		organic1=linkedInOrganicStats,
		organic2=prevlinkedInOrganicStats,
		newFollowers=newFollowers,
		uniqueVisitors=uniqueVisitors,
		organicImpressions=organicImpressions,
		organicImpressionNo=organicImpressionNo,
		organicClicks=organicClicks,
		organicClicksNo=organicClicksNo,
		organicCtr=organicCtr,
		organicCtrNo=organicCtrNo,
		organicShares=organicShares,
		organicSharesNo=organicSharesNo,
		title2=title2,
		title3=title3,
		title4=title4,
		sponsored1=sponsored1,
		sponsored2=sponsored2,
		campaigns=campaigns,
		title5=title5,
		campaignDemos=campaignDemos,
		title6=title6,
		googleCampaignToDate=googleCampaignToDate,
		)

@app.route('/upload', methods=['POST', 'GET'])
def upload():
	# Upload is a function that we use to upload images from the user which are then inserted into the dynamic report using an AJAX script found in ./static/js/scripts.js
	global filename
	if request.method == 'POST':
		print("Method = POST")
		if 'images[]' not in request.files:
			print('images[] not in request files')
			flash('No file part')
			return redirect(request.get().url)

		file = request.files['images[]']
		print("file = request.files['images[]']")
		if file.filename == '':
			print("No filename")
			flash('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			print("if file and allowed_file(file.filename) is true")
			filename = secure_filename(file.filename)
			## This is where it is broken.
			filepath = file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			print("file saved")
			return redirect(url_for('upload', filename=filename))

	imageOutput = "<img src='./static/uploads/"+str(filename)+"'>"
	return imageOutput

@app.route('/google')
def googleauth():
	# googleauth allows the user to refresh the access and refresh tokens for the google-ads api
	# This is step 1 in a multi step process.
	# updateauth.main returns an authorisation URL from google which provides the user the opportunity to consent to the app
	# Google then redirects the user to a page on flagshipmarketing.com which also redirects the user to /googlefinalstep below.
	# This redirect chain contains the tokens required to make requests to the google-ads api.

	### TODO Decrypt secrets file using username and password.

	authUrl = updateauth.main("/code/encrypted_files/secrets.json", "https://www.googleapis.com/auth/adwords", 2555, 'http://localhost/googlefinalstep')
	return redirect(authUrl)

@app.route('/googlefinalstep')
def googleauth2():
	# Using tokens from /google save these elements to the config files that are required to make the calls to google-ads api.

	with open('/code/encrypted_files/secrets.json') as file:
		secrets = json.load(file)
		url = "https://oauth2.googleapis.com/token"
		payload = {
			"client_id": secrets['web']['client_id'],
			"client_secret": secrets['web']['client_secret'],
			"code": request.args['code'],
			"grant_type": "authorization_code",
			"redirect_uri": "http://localhost/googlefinalstep"
		}

		response = requests.post(url, data=payload)
		tokenDict = response.json()
		print(tokenDict, flush=True)

		with open('/code/encrypted_files/google-ads.yaml', "r") as gAdsYaml:
			gAds = yaml.safe_load(gAdsYaml)
			print("GOOGLEADS.YAML", flush=True)
			print(gAds, flush=True)
			gAds['access_token'] = tokenDict['access_token']

			if 'refresh_token' in tokenDict.keys():
				gAds['refresh_token'] = tokenDict['refresh_token']

		with open('/code/encrypted_files/google-ads.yaml', "w") as newgAdsYaml:
			yaml.dump(gAds, newgAdsYaml, default_flow_style=False)

	## TODO re-encrypt google-ads.yaml

	## TODO Run api-call's python main.py then redirect to /output once it is finished loading.

	return tokenDict

@app.route('/linkedinauth')
def linkedinAuth():
	# linkedinAuth generates a new access code for the linkedin ads api which can be exchanged for an access token in /linkedinfinalstep
	# linkedinsecrets.json includes the current linkedin access tokens that are updated in the linkedin authorisation flow
	with open ("./encrypted_files/linkedinsecrets.json") as file:
		data = file.read()
		secrets = json.loads(data)


		responseType = 'code'
		clientId = secrets["clientId"]
		redirectUri = secrets["redirectUri"]
		state = secrets["state"]
		scope = secrets["scope"]

		authenticationRequest = 'https://www.linkedin.com/oauth/v2/authorization?response_type='+ responseType + '&client_id=' + clientId + '&redirect_uri=' +  redirectUri + '&state=' + state + '&scope=' + scope

		# Once the user has given their consent, linkedin will redirect them to the url defined in redirectUri. This will in turn redirect them to
		# /linkedinfinalstep in order to complete the token exchange
		return redirect(authenticationRequest)

@app.route('/linkedinfinalstep')
def linkedinfinalstep():
	with open ("./encrypted_files/linkedinsecrets.json") as file:
		data = file.read()
		secrets = json.loads(data)

		# code is the code returned from linkedin that can be exchanged for a linkedin access token
		# This code is valid for 30 minutes only and must be generated again if not exchanged for an access token in that time
		# More info on the exchange process can be found in the Linkedin Api documentation here:
		# https://docs.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow?tabs=HTTPS
		code = request.args.get('code')
		payload = {
			"grant_type": "authorization_code",
			"code": code,
			"client_id": secrets["clientId"],
			"client_secret": secrets["clientSecret"],
			"redirect_uri": secrets["redirectUri"]
		}

		headers = {
			"Content-Type": "application/x-www-form-urlencoded"
		}
		response = requests.post('https://www.linkedin.com/oauth/v2/accessToken', headers=headers, data=payload)

		# Write the new access token to the linkedin_access_token.txt file for use in api calls
		with open("./encrypted_files/linkedin_access_token.txt", "w+") as accessTokenFile:
			accessTokenFile.write(response.json()["access_token"])

	return "New Token Updated, please try calling the api for updated data again"

@app.route('/', methods=["POST", "GET"])
def index():
	# This page will eventually become the homepage that the user can use to provide credentials, update settings for the report output
	# currently it has no real functionality
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
		# This call should go to the database to retrieve the relevant data on /output.
		r = requests.get('http://config:5000/api/getconfig', auth=(username, password))
	return render_template('index.html')

# Launch the server
if __name__ == "__main__":
	app.run(debug=False, host='0.0.0.0', port=80)
