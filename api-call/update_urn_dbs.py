import json
import functions
import requests
import config

def getRegions():
	response = requests.get('https://api.linkedin.com/v2/regions?',
		headers = {'Authorization': 'Bearer ' + config.access_token
	 	})
	print('Regions Updated')
	a = response.json()
	prettyA = json.dumps(a, indent =2 )
	return prettyA

def getIndustries():
	response =requests.get('https://api.linkedin.com/v2/industries?',
		headers = {'Authorization': 'Bearer ' + config.access_token}
		)
	print('Industries Updated')
	a = response.json()
	prettyA = json.dumps(a, indent =2 )
	return prettyA

def getJobFunctions():
	response =requests.get('https://api.linkedin.com/v2/functions?',
		headers = {'Authorization': 'Bearer ' + config.access_token}
		)
	print('Job Functions Updated')
	a = response.json()
	prettyA = json.dumps(a, indent =2 )
	return prettyA

def getCampaignNames():
	paramsDict = {}
	i = 0
	for campaign in config.campaignURNs:
		paramsDict['ids['+str(i)+']'] = config.campaignURNs[i][25:]
		i+=1

	paramsDict['fields'] = 'name'

	response = requests.get('https://api.linkedin.com/v2/adCampaignsV2?',
		params = paramsDict,
		headers = {'Authorization': 'Bearer ' + config.access_token}
	)
	print('Campaign Names Updated')

	a = response.json()
	prettyA = json.dumps(a, indent =2 )
	return prettyA

def getSeniorities():
	response = requests.get('https://api.linkedin.com/v2/seniorities',
		headers = {'Authorization': 'Bearer ' + config.access_token}
	)

	print('Seniorities Updated')
	a = response.json()
	prettyA = json.dumps(a, indent = 2)
	return prettyA

def getCountries():

	response = requests.get('https://api.linkedin.com/v2/countries',
		headers = {'Authorization': 'Bearer ' + config.access_token}
	)

	print('Countries Updated')
	a = response.json()
	prettyA = json.dumps(a, indent = 2)
	return prettyA

def orgLookup():
	# This function needs to be called after we have the list of 20 organizations URNs for whom we want to find the company names.
	listOfFiles = os.listdir()
	filesWithCompanyURNs = []
	listOfURNs = []
	staticURL = "https://api.linkedin.com/v2/organizationsLookup?ids=List("
	strOfIds = ''

	counter = 0
	for file in listOfFiles:
		if "campaignDemographics" in file:
			counter += 1
			functions.writeToFile(functions.findXHighestResults(file, 20, 'pivotValue', 'impressions'), "top20 "+ file, 'w+')
			filesWithCompanyURNs.append(file[:-5])

	i = 0
	a = 0
	while i < len(filesWithCompanyURNs):
		with open(filesWithCompanyURNs[i]+".json") as json_file:
			companyURNs = json.load(json_file)
		print(len(companyURNs))
		while a < len(companyURNs):
			listOfURNs.append(companyURNs[a]['pivotValue'])
			strOfIds += companyURNs[a]['pivotValue'] + ","
			a+=1
		a = 0
		i += 1

	print(len(strOfIds))

	finalUrl = staticURL + strOfIds + ')'

def main():
	functions.writeToFile(getSeniorities(), 'lookup/_lookUpSeniorities.json', 'w+')
	functions.writeToFile(getCountries(), 'lookup/_lookUpCountries.json', 'w+')
	functions.writeToFile(getCampaignNames(), 'lookup/_lookUpCampaigns.json', 'w+')
	functions.writeToFile(getIndustries(), 'lookup/_lookupIndustries.json', 'w+')
	functions.writeToFile(getRegions(), 'lookup/_lookupRegions.json', 'w+')
	functions.writeToFile(getJobFunctions(), 'lookup/_lookupJobfunctions.json', 'w+')
