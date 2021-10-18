import mysql.connector, json, datetime
import os

f = open("./encrypted_files/config.json", "r")
config = json.loads(f.read())

# JSON file should contain the credentials as a dictionary that can be inserted as the
with open("./encrypted_files/db_cred.json", "r") as db_file:
	db_cred = json.loads(db_file.read())
	mydb = mysql.connector.connect(
	    host = db_cred["host"],
	    user =db_cred["user"],
	    passwd = db_cred["passwd"],
		database = db_cred["database"])
	cursor = mydb.cursor()


def sharesstatictodb():
	with open("/code/data/shares.json") as json_file:
		jsonData = json.load(json_file)

	jsonRecords = []
	i = 1
	for key in jsonData:
		col1 = key['activity']
		col2 = key['text']['text']
		try:
			col3 = key['content']['title']
		except:
			col3 = ""
		try:
			col4 = key['content']['description']
		except:
			col4 = ""
		try:
			col5 = key['content']['shareMediaCategory']
		except:
			col5 = ""
		col6 = key['id']
		record = (col1, col2,col3,col4,col5,col6)
		jsonRecords.append(record)
		i+=1

	sqlCommand = "INSERT INTO posts (post_urn, post_text, post_title, post_description, post_type, post_id) VALUES (%s, %s, %s, %s, %s,%s) ON DUPLICATE KEY UPDATE post_urn=post_urn;"
	cursor.executemany(sqlCommand, jsonRecords)
	mydb.commit()

def ugcstatictodb():

	with open("/code/data/ugc.json") as json_file:
		jsonData = json.load(json_file)

	listOfRecords = []
	for key in jsonData:
		col1 = key['id']
		col2 = key["specificContent"]["com.linkedin.ugc.ShareContent"]["shareCommentary"]["text"]
		try:
			col3 = key['content']['title']
		except:
			col3 = ""
		try:
			col4 = key['content']['description']
		except:
			col4 = ""
		col5 = key["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"]
		col6 = key["id"][15:]
		record = (col1, col2,col3,col4,col5,col6)
		listOfRecords.append(record)

	sqlCommand = "INSERT INTO posts (post_urn, post_text, post_title, post_description, post_type, post_id) VALUES (%s, %s, %s, %s, %s,%s) ON DUPLICATE KEY UPDATE post_id=post_id;"
	cursor.executemany(sqlCommand, listOfRecords)
	mydb.commit()

def sharestemporaltodb():
	now = datetime.datetime.now()
	timestamp = config['dateSettings']['todayddmmyy']

	with open("/code/data/shareStats.json") as json_file:
		jsonData = json.load(json_file)

	cursor.execute("SELECT id, timestamp FROM posts_stats")
	results = cursor.fetchall()
	resultsList = []
	for row in results:
		resultsList.append(row)

	#check if the rows in json already exist in the table with today's date
	# get todays timestamp

	listOfRecords = []
	for key in jsonData:
		col1 = key['share']
		col2 = key['organizationalEntity']
		col3 = key['totalShareStatistics']['shareCount']
		col4 = key['totalShareStatistics']['likeCount']
		col5 = key['totalShareStatistics']['engagement']
		col6 = key['totalShareStatistics']['clickCount']
		col7 = key['totalShareStatistics']['impressionCount']
		if col7 != 0:
			col8 = str(int(col6)/int(col7))
		else:
			col8 = None
		col9 = key['totalShareStatistics']['commentCount']
		col10 = key['share'][13:]
		col11 = str(now.strftime('%d' +'-'+'%m'+'-'+'%Y'))
		col12 = col10+"-"+col11
		record = (col1, col2,col3,col4,col5,col6,col7,col8,col9, col10, col11, col12)
		listOfRecords.append(record)


	for rows in resultsList:
		for records in listOfRecords:
			if rows[0] == records[9] and rows[1] == records[10]:
				listOfRecords.remove(records)
				break

	sqlCommand = "INSERT INTO posts_stats (share_urn, related_org, share_count, like_count, engagement_rate, click_count, impression_count, ctr, comment_count, id, timestamp, unique_timestamp_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE unique_timestamp_id=unique_timestamp_id"
	cursor.executemany(sqlCommand, listOfRecords)
	mydb.commit()

def ugctemporaltodb():

	with open("/code/data/ugcStats.json") as json_file:
		jsonData = json.load(json_file)

	now = datetime.datetime.now()
	timestamp = config['dateSettings']['todayddmmyy']

	cursor.execute("SELECT id, timestamp FROM posts_stats")
	results = cursor.fetchall()
	resultsList = []
	for row in results:
		resultsList.append(row)

	listOfRecords = []
	for key in jsonData['elements']:
		col1 = key['ugcPost']
		col2 = key['organizationalEntity']
		col3 = key['totalShareStatistics']['shareCount']
		col4 = key['totalShareStatistics']['likeCount']
		col5 = key['totalShareStatistics']['engagement']
		col6 = key['totalShareStatistics']['clickCount']
		col7 = key['totalShareStatistics']['impressionCount']
		col8 = key['totalShareStatistics']['commentCount']
		col9 = key['ugcPost'][15:]
		col10 = str(now.strftime('%d' +'-'+'%m'+'-'+'%Y'))
		col11 = col9+"-"+col10
		record = (col1, col2,col3,col4,col5,col6,col7,col8,col9, col10, col11)
		listOfRecords.append(record)

	for rows in resultsList:
		for records in listOfRecords:
			if rows[0] == records[8] and rows[1] == records[9]:
				print("record not updated")
				listOfRecords.remove(records)
				break
	sqlCommand = "INSERT INTO posts_stats (share_urn, related_org, share_count, like_count, engagement_rate, click_count, impression_count, comment_count, id, timestamp,unique_timestamp_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s) ON DUPLICATE KEY UPDATE unique_timestamp_id=unique_timestamp_id"
	cursor.executemany(sqlCommand, listOfRecords)
	mydb.commit()

def sponsoredcampaignsdemostodb(campaignId):

	with open("/code/data/campaignDemographics - "+campaignId+".json") as json_file:
		jsonData = json.load(json_file)

	sqlQuery = "SELECT campaign_id, timestamp, related_org FROM sponsored_campaign_demos WHERE campaign_id=" + campaignId
	cursor.execute(sqlQuery)
	results = cursor.fetchall()
	resultsList = []
	for row in results:
		resultsList.append(row)

	now = datetime.datetime.now()

	listOfRecords = []
	for key in jsonData:
		col1 = campaignId
		col2 = key['shares']
		col3 = key['pivotValue']
		col4 = key['comments']
		col5 = key['follows']
		col6 = key['companyPageClicks']
		col7 = key['clicks']
		col8 = key['costInLocalCurrency']
		col9 = key['reactions']
		col10 = key['impressions']
		col11 = key['approximateUniqueImpressions']
		col12 = str(now.strftime('%d' +'-'+'%m'+'-'+'%Y'))
		col13 = col1 + "-" +col3[19:] + "-"+col12
		record = (col1, col2,col3,col4,col5,col6,col7,col8,col9, col10, col11, col12,col13)
		listOfRecords.append(record)


	sqlCommand = "INSERT INTO sponsored_campaign_demos (campaign_id, shares, related_org, comments, follows, page_clicks, clicks, cost, reactions, impressions, approx_unique_impressions, timestamp, unique_timestamp_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s,%s) ON DUPLICATE KEY UPDATE unique_timestamp_id=unique_timestamp_id"
	cursor.executemany(sqlCommand, listOfRecords)
	mydb.commit()

def getlistofcampaigns():
	datafiles = os.listdir("/code/data/")
	campaignList = []
	for file in datafiles:
		if "campaignDemographics" in file:
			campaignList.append(file[23:-5])
	for campaign in campaignList:
		sponsoredcampaignsdemostodb(campaign)

def linkedinsponsoreddatadynamic():

	with open("/code/data/linkedinSponsoredData.json") as json_file:
		jsonData = json.load(json_file)

	now = datetime.datetime.now()

	listOfRecords = []
	for key in jsonData['elements']:

		col1 = key['pivotValue'][25:]
		col2 = key['shares']
		col3 = key['comments']
		col4 = key['follows']
		col5 = key['companyPageClicks']
		col6 = key['clicks']
		col7 = key['costInLocalCurrency']
		col8 = key['reactions']
		col9 = key['impressions']
		col10 = key['approximateUniqueImpressions']
		col11 = str(now.strftime('%d' +'-'+'%m'+'-'+'%Y'))
		col12 = col1 + "-"+ col11
		record = (col1, col2,col3,col4,col5,col6,col7,col8,col9, col10,col11, col12)
		listOfRecords.append(record)

	sqlCommand = "INSERT INTO ln_sponsored_stats (campaign_id, shares, comments, follows, page_clicks, clicks, cost, reactions, impressions, approx_unique_impressions, timestamp, unique_timestamp_id) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s) ON DUPLICATE KEY UPDATE unique_timestamp_id=unique_timestamp_id"
	cursor.executemany(sqlCommand, listOfRecords)
	mydb.commit()


def followerdemosbyregion():
	with open("/code/data/followerDemographics.json") as json_file:
		jsonData = json.load(json_file)

	now = datetime.datetime.now()

	listOfRecords = []
	for key in jsonData['elements'][0]['followerCountsByRegion']:
		col1 = key['region']
		col2 = key['followerCounts']['organicFollowerCount']
		col3 = key['followerCounts']['paidFollowerCount']
		col4 = col2 + col3
		col5 = str(now.strftime('%d' +'-'+'%m'+'-'+'%Y'))
		col6 = col1 +"-" + col5
		record = (col1, col2,col3,col4,col5,col6)
		listOfRecords.append(record)

	sqlCommand = "INSERT INTO follower_demos_region (region_id, organic_followers, paid_followers, total_followers,timestamp,unique_timestamp_id) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE unique_timestamp_id=unique_timestamp_id"
	cursor.executemany(sqlCommand, listOfRecords)
	mydb.commit()

def followerdemosbyseniority():
	with open("/code/data/followerDemographics.json") as json_file:
		jsonData = json.load(json_file)

	now = datetime.datetime.now()

	listOfRecords = []
	for key in jsonData['elements'][0]['followerCountsBySeniority']:
		col1 = key['seniority']
		col2 = key['followerCounts']['organicFollowerCount']
		col3 = key['followerCounts']['paidFollowerCount']
		col4 = col2 + col3
		col5 = str(now.strftime('%d' +'-'+'%m'+'-'+'%Y'))
		col6 = col1 +"-" + col5
		record = (col1, col2,col3,col4,col5,col6)
		listOfRecords.append(record)

	sqlCommand = "INSERT INTO follower_demos_seniority (seniority_id, organic_followers, paid_followers, total_followers,timestamp,unique_timestamp_id) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE unique_timestamp_id=unique_timestamp_id"
	cursor.executemany(sqlCommand, listOfRecords)
	mydb.commit()


def followerdemosbyindustry():
	with open("/code/data/followerDemographics.json") as json_file:
		jsonData = json.load(json_file)

	now = datetime.datetime.now()

	listOfRecords = []
	for key in jsonData['elements'][0]['followerCountsByIndustry']:
		col1 = key['industry']
		col2 = key['followerCounts']['organicFollowerCount']
		col3 = key['followerCounts']['paidFollowerCount']
		col4 = col2 + col3
		col5 = str(now.strftime('%d' +'-'+'%m'+'-'+'%Y'))
		col6 = col1 +"-" + col5
		record = (col1, col2,col3,col4,col5,col6)
		listOfRecords.append(record)

	sqlCommand = "INSERT INTO follower_demos_industry (industry_id, organic_followers, paid_followers, total_followers,timestamp, unique_timestamp_id) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE unique_timestamp_id=unique_timestamp_id"
	cursor.executemany(sqlCommand, listOfRecords)
	mydb.commit()

def followerdemosbyfunction():
	with open("/code/data/followerDemographics.json") as json_file:
		jsonData = json.load(json_file)

	now = datetime.datetime.now()

	listOfRecords = []
	for key in jsonData['elements'][0]['followerCountsByFunction']:
		col1 = key['function']
		col2 = key['followerCounts']['organicFollowerCount']
		col3 = key['followerCounts']['paidFollowerCount']
		col4 = col2 + col3
		col5 = str(now.strftime('%d' +'-'+'%m'+'-'+'%Y'))
		col6 = col1 +"-" + col5
		record = (col1, col2,col3,col4,col5,col6)
		listOfRecords.append(record)

	sqlCommand = "INSERT INTO follower_demos_job_function (function_id, organic_followers, paid_followers, total_followers,timestamp,unique_timestamp_id) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE unique_timestamp_id=unique_timestamp_id"
	cursor.executemany(sqlCommand, listOfRecords)
	mydb.commit()


def followerdemosbystaffcount():
	with open("/code/data/followerDemographics.json") as json_file:
		jsonData = json.load(json_file)

	now = datetime.datetime.now()

	listOfRecords = []
	for key in jsonData['elements'][0]['followerCountsByStaffCountRange']:
		col1 = key['staffCountRange']
		col2 = key['followerCounts']['organicFollowerCount']
		col3 = key['followerCounts']['paidFollowerCount']
		col4 = col2 + col3
		col5 = str(now.strftime('%d' +'-'+'%m'+'-'+'%Y'))
		col6 = col1 +"-" + col5
		record = (col1, col2,col3,col4,col5,col6)
		listOfRecords.append(record)

	sqlCommand = "INSERT INTO follower_demos_staff_count (staffCountRange, organic_followers, paid_followers, total_followers,timestamp, unique_timestamp_id) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE unique_timestamp_id=unique_timestamp_id"
	cursor.executemany(sqlCommand, listOfRecords)
	mydb.commit()

def followerdemobycountry():


	with open("/code/data/followerDemographics.json") as json_file:
		jsonData = json.load(json_file)

	now = datetime.datetime.now()

	listOfRecords = []

	for key in jsonData['elements'][0]['followerCountsByCountry']:
		col1 = key['country']
		col2 = key['followerCounts']['organicFollowerCount']
		col3 = key['followerCounts']['paidFollowerCount']
		col4 = col2 + col3
		col5 = str(now.strftime('%d' +'-'+'%m'+'-'+'%Y'))
		col6 = col1 +"-" + col5
		record = (col1, col2, col3, col4, col5, col6)
		listOfRecords.append(record)

	sqlCommand = "INSERT INTO follower_demos_country (country_id, organic_followers, paid_followers, total_followers, timestamp, unique_timestamp_id) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE unique_timestamp_id=unique_timestamp_id"
	cursor.executemany(sqlCommand, listOfRecords)
	mydb.commit()


def pagestatstodb():

	with open("/code/data/pagestats.json") as json_file:
		jsonData = json.load(json_file)

	listOfRecords = []
	uniqueSum = 0
	for key in jsonData['elements']:

		col1 = key['organization']
		col2 = str(datetime.datetime.fromtimestamp(key['timeRange']['end']/1000).strftime('%Y-%m-%d'))
		col3 = key['totalPageStatistics']['views']['allPageViews']['pageViews']
		col4 = key['totalPageStatistics']['views']['allPageViews']['uniquePageViews']

		uniqueSum = uniqueSum + col4

		record = (col1, col2, col3, col4)
		listOfRecords.append(record)

	sqlCommand = "INSERT INTO page_stats (org_id, timestamp, page_views, unique_page_views) VALUES (%s, %s, %s,%s) ON DUPLICATE KEY UPDATE timestamp=timestamp"
	cursor.executemany(sqlCommand, listOfRecords)
	mydb.commit()

def insertGoogleRecords():
	with open("/code/data/google_data.json") as file:
		now = datetime.datetime.now()
		data = file.read()
		output = json.loads(data)
		listOfRecords = []
		for key in output[0]:
			col1 = key[1]
			col2 = key[2][1:].replace(',','')
			col3 = key[3].replace(',','')
			col4 = key[4].replace(',','')
			col5 = key[7]
			col6 = str(now.strftime('%d' +'-'+'%m'+'-'+'%Y'))
			col7 = key[0]
			record = (col1, col2, col3, col4, col5, col6, col7)
			listOfRecords.append(record)

		print(listOfRecords)
		sqlCommand = "INSERT INTO google_spons (campaign_name, cost, impressions, clicks, conversions, timestamp, campaign_status) VALUES (%s, %s, %s, %s, %s, %s, %s)"
		cursor.executemany(sqlCommand, listOfRecords)
		mydb.commit()

def closeConnection():
	cursor.close()
	mydb.close()


def update():

	sharesstatictodb()
	print("Static Shares Records Updated")
	ugcstatictodb()
	print("Video Shares Records Updated")
	sharestemporaltodb()
	print("Static Shares Temporal Records Updated")
	ugctemporaltodb()
	print("Video Shares Temporal Records Updated")
	getlistofcampaigns()
	print("Campaign URNs Retrieved")
	linkedinsponsoreddatadynamic()
	print("LinkedIn Sponsored Records Updated")
	followerdemosbyregion()
	print("Follower Demographics by Region Updated")
	followerdemosbyseniority()
	print("Follower Demographics by Seniority Updated")
	followerdemosbyindustry()
	print("Follower Demographics by Industry Updatedmydb")
	followerdemosbyfunction()
	print("Follower Demographics by Function Updated")
	followerdemosbystaffcount()
	print("Follower Demographics by Staff Count Updated")
	followerdemobycountry()
	print("Follower Demographics by Country Updated")
	pagestatstodb()
	print("Company Page Stats Updated")
	insertGoogleRecords()
	print("Google Stats Updated")
	closeConnection()
	print("Connection Closed")
