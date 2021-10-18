import requests
import json
from datetime import date, datetime
import ast
import functions
import db_functions

global access_token

with open("/code/encrypted_files/linkedin_access_token.txt") as file:
	access_token = str.rstrip(file.read())
print("Linkedin access token = " + access_token, flush =True)

with open("./encrypted_files/config.json") as configFile:
	config = json.loads(configFile.read())

def getSharesByOrg():
	# Returns shares with text, titles, descriptions and URNs but no stats for the posts.
	global listOfShareIds

	listOfShareIds = []
	index = 0
	sharesReturned = []
	lengthOfShares = 1

	while lengthOfShares > 0:
		# Get list of share IDs and add them to listOfShareIds
		response = requests.get('https://api.linkedin.com/v2/shares?',
			params = {
			'q' : 'owners',
			'owners': config["companyIDs"]["companyURN"],
			'sortBy': 'CREATED',
			'sharesPerOwner': '1000',
			'count': '100',
			'start': index,
			'fields': 'activity,id,content:(title,description,shareMediaCategory),created:(time),text:(text),edited'
			},
			headers = {
			'Authorization': 'Bearer ' + access_token,
			})

		print(response, flush=True)
		allShares = response.json()
		shares = []

		# Filter shares that are before campaign start date
		i = 0
		while i < len(allShares['elements']):
			if allShares['elements'][i]['created']['time'] > int(config["dateSettings"]["organicStartDate"]):
				shares.append(allShares['elements'][i])
				listOfShareIds.append('urn:li:share:' + allShares['elements'][i]['id'])
			i += 1

		lengthOfShares = len(shares)

		for share in shares:
			sharesReturned.append(share)

		index += 100

	prettyA = json.dumps(sharesReturned, indent=2)
	return prettyA

def getSponsoredCreativeNames(campaignNumber):

	response  = requests.get("https://api.linkedin.com/v2/adCreativesV2?",
	params = {
	"q":"search",
	"search.campaign.values[0]": "urn:li:sponsoredCampaign:"+str(campaignNumber),
	"search.test":"false"
	},
	headers = {
	'Authorization': 'Bearer ' + access_token,
	})

	print("Retriving creatives for campaign "+ campaignNumber)

	json_response = response.json()

	elements  = json_response['elements']
	output = json.dumps(elements, indent = 2)
	return output

def getUGCsByOrg():
	# Returns the json of video posts with titles and URNs but no post stats.
	global listOfUGCIds
	listOfUGCIds = []

	# Get list of UGCPost IDs and add them to listOfUGCIds
	responseB = requests.get('https://api.linkedin.com/v2/ugcPosts?q=authors&authors=List('+config["companyIDs"]["companyURN"].replace(":","%3A")+')&fields=id,created:(time),specificContent:(com.linkedin.ugc.ShareContent)&count=100&sortBy=CREATED',
		params = {
		},
		headers = {
		'Authorization': 'Bearer ' + access_token,
		'X-Restli-Protocol-Version' : '2.0.0'
		})

	B = responseB.json()
	refinedUGCData = []
	h = 0
	while h < len(B['elements']):
		if str(B['elements'][h]['specificContent']['com.linkedin.ugc.ShareContent']['shareMediaCategory']) == 'VIDEO' and B['elements'][h]['created']['time'] > int(config["dateSettings"]["organicStartDate"]):
			listOfUGCIds.append(B['elements'][h]['id'])
			refinedUGCData.append(B['elements'][h])
		h += 1

	prettyA = json.dumps(refinedUGCData, indent=2)
	return prettyA

def getSharesStats():

	# create the shares dict from listOfShareIds
	# we need to break the call up into chunks of 100 shares at a time (otherwise LinkedIn returns a 500 Server error)

	# max limit of a single call:
	limit = 100

	## This example of list comprehension comes from geeksforgeeks.org. The following comments are my (JD) notes to help me understand how it does that.
	# We're going to break down listofshareids into a list of lists that have a max length of 100

	# listOfShareIds[i*limit : (i+1)*limit] for the first time round the for loop, this evaluates to:
	# listOfShareIds[0*100:1*100] - This makes it clear that we're looking at a slice of the initial list from 0-100
	# On the second loop, it evaluates to listOfShareIds[100:200] getting us our second list and so on.

	# The loop itself works like this:
	# On the first time round, it evaluates to:
	# for i in range((101 + 100 -1) // 100)
	# for i in range((200) // 100)
	# for i in range(2)

	# This gives us the number of lists that we will need in our metalist by:
	# 1) taking the total length of the initial list
	# 2) taking the max length of the list minus 1
	# This gives the total number of "spaces" we would require across the total number of lists output
	# 3) We divide these spaces by the max limit of spaces per list
	# (integer divide because we don't care about fractions of a list)

	listOfListOfShareIds = [listOfShareIds[i*limit : (i+1)*limit] for i in range((len(listOfShareIds) + limit-1) // limit)]
	output = []
	payload = {'q':'organizationalEntity',
				'organizationalEntity':config["companyIDs"]["companyURN"] }
	i = 0
	while i < len(listOfListOfShareIds):
		a = 0
		while a < len(listOfListOfShareIds[i]):
		   payload['shares[' + str(a) + ']' ] = listOfListOfShareIds[i][a]
		   a += 1

		# Create API request (Originally this was query tunneling due to length of payload, although that was
		# Causing an issue with the length of the request, so it has been changed to simply call the API
		# as many times as it needs and combining the output at the end of the loop
		response = requests.post('https://api.linkedin.com/v2/organizationalEntityShareStatistics?',
			params = payload,
			headers = {
				'X-HTTP-Method-Override': 'GET',
				'Authorization': 'Bearer ' + access_token,
				'Content-Type': 'application/x-www-form-urlencoded'}
				)

		# Don't forget to reset payload! ;)
		payload = {'q':'organizationalEntity',
					'organizationalEntity':config["companyIDs"]["companyURN"] }



		shareStatsList = response.json()
		for post in shareStatsList['elements']:
			output.append(post)

		i += 1

	finalOutput = json.dumps(output, indent = 2)
	return finalOutput

def getUGCStats():
	# create the UGCs dict from listOfUGCIds
	payload = {'q':'organizationalEntity', 'organizationalEntity':config["companyIDs"]["companyURN"],}
	i = 0
	while i < len(listOfUGCIds):
		payload['ugcPosts[' + str(i) + ']' ] = listOfUGCIds[i]
		i += 1

	# Create API request (Query Tunneling due to length of payload)
	response = requests.post('https://api.linkedin.com/v2/organizationalEntityShareStatistics?',
		params = payload,
		headers = {
			'X-HTTP-Method-Override': 'GET',
			'Authorization': 'Bearer ' + access_token,
			'Content-Type': 'application/x-www-form-urlencoded'}
			)

	# Write to json and output
	UGCStatsList = response.json()
	output = json.dumps(UGCStatsList, indent = 2)
	return output

def followerStatsLastXDays(numberOfDays):
	#We will need to fix this when there is an error in the manipulation of the data from followerStatsLast30Days.json
	timeRangeStart = functions.datetimeToMs(datetime.today()) - (numberOfDays * config["dateSettings"]["dayInMs"])

	response = requests.get('https://api.linkedin.com/v2/organizationalEntityFollowerStatistics?',
		params = {
		'q' : 'organizationalEntity',
		'organizationalEntity': config["companyIDs"]["companyURN"],
		'timeIntervals.timeGranularityType': 'DAY',
		'timeIntervals.timeRange.start': timeRangeStart,
		},
		headers = {'Authorization': 'Bearer ' + access_token})

	a = response.json()
	prettyA = json.dumps(a, indent=2)
	return prettyA

def followerStatsByDemo():
	response = requests.get('https://api.linkedin.com/v2/organizationalEntityFollowerStatistics?',
		params = {
		'q' : 'organizationalEntity',
		'organizationalEntity': config["companyIDs"]["companyURN"],
		},
		headers = {'Authorization': 'Bearer ' + access_token})

	a = response.json()
	prettyA = json.dumps(a, indent=2)
	return prettyA

def sponsoredDataTotal():
	# This function makes three calls to the LinkedIn API.
	# First it gets all the names of the campaigns in the supplied accounts
	# Then it gets the stats for all time up to 14 days ago and writes that to linkedinSponsoredDataLastReport.json
	# Finally the function returns the stats for all time up to the current time.
	## TODO is it possible to get the names in one of the other calls so we don't have to ping them twice?
	## TODO Resolve the case that this fails when the campaign is live less than 14 days.
	###DEBUGGING###
	with open("/code/encrypted_files/linkedin_access_token.txt") as file:
		access_token = str.rstrip(file.read())
	###DEBUGGING###


	response1 = requests.get('https://api.linkedin.com/v2/adCampaignsV2?',
		 params = {
			'q': 'search',
			'search.account.values[0]':config["sponsoredAccountURN"],
			'fields':'name,campaignGroup,id,',
		 },
		 headers = {'Authorization': 'Bearer ' + access_token
		 })

	b = response1.json()
	prettyB = json.dumps(b, indent =2)
	functions.writeToFile(prettyB, config["linkedin"]["datafiles"] + 'campaignNames.json', 'w+')


	# Check if the startdate is less than or enqual to the currentTimeMinusTimeDeltaInMs and if it is then don't make this call

	if int(config['dateSettings']['sponsoredStartDate']) <= functions.currentTimeMinusTimeDeltaInMs():
		response2 = requests.get('https://api.linkedin.com/v2/adAnalyticsV2?',
			 params = {
				'q': 'analytics',
				'dateRange.start.year': functions.sponsoredStartdate().strftime('%Y'),
				'dateRange.start.month' : functions.sponsoredStartdate().strftime('%m'),
				'dateRange.start.day' : functions.sponsoredStartdate().strftime('%d'),
				'dateRange.end.year': str(functions.currentTimeMinusTimeDeltaInDatetime().strftime('%Y')),
				'dateRange.end.month' : str(functions.currentTimeMinusTimeDeltaInDatetime().strftime('%m')),
				'dateRange.end.day' : str(functions.currentTimeMinusTimeDeltaInDatetime().strftime('%d')),
				'timeGranularity': 'ALL',
				'accounts': config["sponsoredAccountURN"],
				'pivot':'CAMPAIGN',
				'fields':'impressions,clicks,shares,comments,costInLocalCurrency,follows,reactions,pivotValue,companyPageClicks,approximateUniqueImpressions,'
			 },
			 headers = {'Authorization': 'Bearer ' + access_token})

		c = response2.json()
		prettyC = json.dumps(c, indent = 2)
		functions.writeToFile(prettyC,config["linkedin"]["datafiles"] + 'linkedinSponsoredDataLastReport.json','w+')

	response3 = requests.get('https://api.linkedin.com/v2/adAnalyticsV2?',
		 params = {
			'q': 'analytics',
			'dateRange.start.year': functions.sponsoredStartdate().strftime('%Y'),
			'dateRange.start.month' : functions.sponsoredStartdate().strftime('%m'),
			'dateRange.start.day' : functions.sponsoredStartdate().strftime('%d'),
			'dateRange.end.year': str(datetime.today().year),
			'dateRange.end.month' : str(datetime.today().month),
			'dateRange.end.day' : str(datetime.today().day),
			'timeGranularity': 'ALL',
			'accounts': config["sponsoredAccountURN"],
			'pivot':'CAMPAIGN',
			'fields':'impressions,clicks,shares,comments,costInLocalCurrency,follows,reactions,pivotValue,companyPageClicks,approximateUniqueImpressions'
		 },
		 headers = {'Authorization': 'Bearer ' + access_token
		 }
		 )

	a = response3.json()
	prettyA = json.dumps(a, indent =2 )
	return prettyA

def campaignDemographics(campaignURN):
	response = requests.get('https://api.linkedin.com/v2/adAnalyticsV2?',
		 params = {
			'q': 'analytics',
			'dateRange.start.year': functions.sponsoredStartdate().strftime('%Y'),
			 'dateRange.start.month' : functions.sponsoredStartdate().strftime('%m'),
			'dateRange.start.day' : functions.sponsoredStartdate().strftime('%d'),
			'dateRange.end.year': str(datetime.today().year),
			 'dateRange.end.month' : str(datetime.today().month),
			'dateRange.end.day' : str(datetime.today().day),
			 'timeGranularity': 'ALL',
			 'pivot': 'MEMBER_COMPANY',
			 'campaigns': campaignURN,
			'fields':'impressions,clicks,shares,comments,costInLocalCurrency,follows,reactions,pivotValue,companyPageClicks,approximateUniqueImpressions,'
		 },
		 headers = {'Authorization': 'Bearer ' + access_token}
		 )

	a = response.json()
	prettyA = json.dumps(a['elements'], indent = 2)
	functions.writeToFile(prettyA, config["linkedin"]["datafiles"] + 'campaignDemographics - '+ campaignURN[25:] +'.json','w+')
	print("Campaign Demographics for " + campaignURN[-9:] + " created")

def pageStatistics():

	response = requests.get('https://api.linkedin.com/v2/organizationPageStatistics?',
		params = {
		'q': 'organization',
		'organization': config["companyIDs"]["companyURN"],
		'timeIntervals.timeGranularityType' : 'DAY',
		'timeIntervals.timeRange.start': functions.currentTimeMinusTimeDeltaInMs(),
		'timeIntervals.timeRange.end': functions.datetimeToMs(datetime.today())
		},
		headers = {'Authorization': 'Bearer ' + access_token
		 })

	# print("Initial connection response code: " + response.code)

	a = response.json()
	prettyA = json.dumps(a, indent =2 )
	return prettyA

def getOrgNames(listOfURNs):

	with open("/code/encrypted_files/linkedin_access_token.txt") as file:
		access_token = file.read()

	orgURNsString = ""

	for urn in listOfURNs:
		orgURNsString += str(urn[20:]) + ","

	# make our call to linkedin with the URNs in listofURNs to get the their names
	response = requests.get('https://api.linkedin.com/v2/organizationsLookup?ids=List('+orgURNsString[:-1]+')',
	params = {
		'fields':'localizedName'
	},
	headers = {
		'Authorization': 'Bearer ' + access_token,
		'X-Restli-Protocol-Version': '2.0.0'})
	print("Company numbers: "+orgURNsString[:-1]+' retrieved')


	jsonNames = response.json()
	try:
		listOfResults = []
		for urn in listOfURNs:
			localName = jsonNames['results'][urn[20:]]['localizedName']
			listOfResults.append(localName)
	except:
		print("Error retrieving Org Names")
		print(response.status_code)
		print(response.text)

	return listOfResults


def campaignDemographicsLoop():
	with open("/code/lookup/_lookUpCampaigns.json") as json_file:
		campaigns = json.load(json_file)

	for key in campaigns['results']:
		campaignDemographics("urn:li:sponsoredCampaign:"+key)


def writeAndLog(filename, function):
	logUpdates =[] #DEBUGGING
	functions.writeToFile(function, filename, 'w+')
	DMY = str(datetime.now().strftime("%A %d %B %Y"))
	HMS = str(datetime.now().strftime("%H-%M-%S"))
	updatedDict = {'filename' : filename, "last_updated" : DMY + " - " + HMS}
	logUpdates.append(updatedDict)

def demosByCampaignandCompany(listOfCampaignURNs):
	data = []
	# For each campaign
	for campaign in listOfCampaignURNs:
		campaignID = str(campaign[-9:])
		campaignData = db_functions.buildCampaignTables(campaignID,"impressions")

		listOfURNs = []
		for urn in campaignData:
			listOfURNs.append(str(urn[2]))
		listOfLocalizedNames = getOrgNames(listOfURNs)

		# get the total impressions so we can calculate percentage of total impressions per org per campaign
		sumImpressions = 0
		for datapoint in campaignData:
			sumImpressions += datapoint[3]

		# processedData = [['Company','CampaignID', 'Impressions', 'Percentage of Total Impressions']]
		processedData = []
		processedDatapoint = []
		index = 0
		# Calculate the percentage of total impressions each org (datapoint) has for each campaign
		for datapoint in campaignData:
			percentageOfImpressions = str(round(datapoint[3]/sumImpressions,2))+"%"
			## append the new datapoint to the inner list (representing a row in the final table)
			# add the localized names of the company to the datapoint
			processedDatapoint.append(listOfLocalizedNames[index])
			# for each element in datapoint, append this element to a new list called processedDatapoint.
			for element in datapoint:
				if str(element) != str(campaignID) and "urn:" not in str(element):
					processedDatapoint.append(str(element))
			# then add the percentage of impressions to that datapoint
			processedDatapoint.append(percentageOfImpressions)

			#now add the whole datapoint to the processed data set and start again
			processedData.append(processedDatapoint)

			#clear processed datapoint
			processedDatapoint = []

			index += 1
		data.append(processedData)
	index = 0
	output = json.dumps(data, indent = 2)
	return output

def main():
	global logUpdates
	global access_token
	global config
	logUpdates =[]

	f = open("config.json", "r")
	config = json.loads(f.read())

	with open("/code/encrypted_files/linkedin_access_token.txt") as file:
		access_token = str.rstrip(file.read())

	print("Creating data files")
	writeAndLog(config["linkedin"]["datafiles"] + 'pagestats.json', pageStatistics())
	print("Pagestats.json created")
	writeAndLog(config["linkedin"]["datafiles"] + 'followerStatsLastXDays.json', followerStatsLastXDays(30))
	print("followerStatsLastXDays.json created")
	writeAndLog(config["linkedin"]["datafiles"] + 'followerDemographics.json', followerStatsByDemo())
	print("followerDemographics.json created")
	writeAndLog(config["linkedin"]["datafiles"] + 'linkedinSponsoredData.json', sponsoredDataTotal())
	print("linkedinSponsoredData.json created")
	writeAndLog(config["linkedin"]["datafiles"] + 'shares.json', getSharesByOrg())
	print("shares.json created")
	writeAndLog(config["linkedin"]["datafiles"] + 'ugc.json', getUGCsByOrg())
	print("ugc.json Created")
	writeAndLog(config["linkedin"]["datafiles"] + 'shareStats.json', getSharesStats())
	print("shareStats.json created")
	writeAndLog(config["linkedin"]["datafiles"] + 'ugcStats.json', getUGCStats())
	print("ugcStats.json created")
	campaignDemographicsLoop()
	print("Campaign Demographics Started")

	creativeJsonString = "["
	for campaign in config['campaignIDs']['campaignNumbers']:
		creativeJsonString += getSponsoredCreativeNames(campaign) + ","
	creativeJsonString = creativeJsonString[:-1]
	creativeJsonString += "]"
	writeAndLog(config["linkedin"]["datafiles"] + 'creatives.json', creativeJsonString)

	print("All data files created.")

	# Update the log file to make sure that the stats are reasonably up to date.
	DMY = str(datetime.now().strftime("%A %d %B %Y"))
	HMS = str(datetime.now().strftime("%H-%M-%S"))
	logFileName = DMY + " "+ HMS + " Update Log.json"
	logUpdateJson = json.dumps(logUpdates, indent = 2)
