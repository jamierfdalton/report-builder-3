import mysql.connector, json, datetime
import os
import requests

# r = requests.get('http://config:5000/api/getconfig')
# config = json.loads(r.text)

def dbconnect():
	# Connect to the database or provide a connection error if the credentials contained in db_cred.json are incorrect.
	# The JSON file contains the credentials as a dictionary that can be inserted into the db connection functions
	with open("./encrypted_files/db_cred.json", "r") as db_file:
		db_cred = json.loads(db_file.read())

		config = {
			"host": db_cred["host"],
			"user": db_cred["user"],
			"passwd": db_cred["passwd"],
			"database": db_cred["database"]
			}

		try:
			c = mysql.connector.connect(**config)
			return c
		except:
			print("Database Connection error", flush=True)
			exit(1)

def followerGain30Days():
	# TODO Make followerGain30Days dateranges dynamic

	# Returns the number of followers for the last 30 days.
	db = dbconnect()
	db_cursor = db.cursor()

	sqlCommand  = "SELECT (SELECT SUM(follower_demos_country.total_followers) FROM follower_demos_country WHERE timestamp='21-06-2021')-(SELECT SUM(follower_demos_country.total_followers) FROM follower_demos_country WHERE timestamp='22-05-2021')"

	db_cursor.execute(sqlCommand)
	followerCount = db_cursor.fetchall()
	db.close()

	return followerCount[0][0]

def getdemosbycompany(listOfCampaigns):
	# Returns a list of companies per campaign ordered by the greatest to least number of impressions generated by that company.
	# listOfCampagins argument is a list of campaignURNs as strings.
	# CampaignURNs are a linkedin format for identifying campaigns they have the following format: "urn:li:sponsoredCampaign:"111111111"
	db = dbconnect()
	db_cursor = db.cursor()

	output = []
	for campaign in listOfCampaigns:
		sqlCommand = "SELECT demos_by_company.campaign_name, company_name, impressions, percentage_of_impressions from demos_by_company inner join campaigns on demos_by_company.campaign_name=campaigns.campaign_name where campaigns.campaign_id ='"+campaign[-9:]+"'"
		db_cursor.execute(sqlCommand)
		results = db_cursor.fetchall()
		results.insert(0, ["Campaign Name", "Company", "Impressions", "Percentage of Total Impressions"])
		output.append(results)

	db.close()
	return output

def getSumOfLinkedInOrganicStats(date):
	# Returns a list of stats relating to Linkedin organic posts from the date given as a string in the format 'dd-mm-yyyy'
	db = dbconnect()
	db_cursor = db.cursor()

	sqlCommand = "SELECT SUM(`impression_count`), SUM(`comment_count`), SUM(`like_count`), SUM(`click_count`), SUM(`share_count`), COUNT(`impression_count`) FROM `posts_stats` WHERE `timestamp`='"+date+"' AND `impression_count`> 100"
	db_cursor.execute(sqlCommand)

	fetchedStats = db_cursor.fetchmany()

	## Error handling in the case that the date requested doesn't exist in the database.
	if fetchedStats[0][0] == None:

		sqlCommand = "SELECT DISTINCT timestamp FROM reportbuilder.posts_stats"
		db_cursor.execute(sqlCommand)
		tupleTimestamps = db_cursor.fetchall()

		timestamps = []
		for time in tupleTimestamps:
			# Take the list of tuples, turn them into datetime and make them into a less unwieldy list
			strToDatetime = datetime.datetime.strptime(time[0],'%d-%m-%Y')
			timestamps.append(strToDatetime)

		# Turn date to datetime
		date = datetime.datetime.strptime(date,'%d-%m-%Y')

		# Find the closest date in timestamps to the date provided in the function call
		newDate = min(timestamps, key=lambda sub: abs(sub - date))

		# Change back to a string
		date = newDate.strftime('%d-%m-%Y')

		# Retrieve data from the database with the new date.
		sqlCommand = "SELECT SUM(`impression_count`), SUM(`comment_count`), SUM(`like_count`), SUM(`click_count`), SUM(`share_count`), COUNT(`impression_count`) FROM `posts_stats` WHERE `timestamp`='"+date+"' AND `impression_count`> 100"
		db_cursor.execute(sqlCommand)

		fetchedStats = db_cursor.fetchmany()

	results = [date,]

	results.append(str("{:,}".format(fetchedStats[0][0])))
	results.append(str("{:,}".format(fetchedStats[0][1])))
	results.append(str("{:,}".format(fetchedStats[0][2])))
	results.append(str("{:,}".format(fetchedStats[0][3])))
	results.append(str("{:,}".format(round((fetchedStats[0][3]/fetchedStats[0][0])*100,2)))+"%")
	results.append(str("{:,}".format(fetchedStats[0][4])))
	results.append(str("{:,}".format(fetchedStats[0][5])))
	results.append(str("{:,}".format(round((fetchedStats[0][0]/fetchedStats[0][5]),0))))
	results.append(str("{:,}".format(round((fetchedStats[0][4]/fetchedStats[0][5]),0))))

	db.close()

	return results

def getSumOfLinkedInSponsoredStats(date):
	# Returns a list of summed stats for all linkedin sponsored campaigns at the given date
	# date is a string in the format "dd-mm-yyyy"
	db = dbconnect()
	db_cursor = db.cursor()

	sqlCommand = "SELECT `ln_sponsored_stats`.`campaign_id`, `campaigns`.`campaign_name`, SUM(`cost`), SUM(`impressions`), SUM(`clicks`), SUM(`approx_unique_impressions`), SUM(`follows`), SUM(`page_clicks`), `timestamp` FROM `ln_sponsored_stats` INNER JOIN `campaigns` ON `ln_sponsored_stats`.`campaign_id`=`campaigns`.`campaign_id` WHERE `timestamp` = '"+date+"' GROUP BY `id`"
	db_cursor.execute(sqlCommand)
	fetchedStats = db_cursor.fetchall()

	## Error handling in the case that the date requested doesn't exist in the database.
	if fetchedStats == []:

		sqlCommand = "SELECT DISTINCT timestamp FROM reportbuilder.posts_stats"
		db_cursor.execute(sqlCommand)
		tupleTimestamps = db_cursor.fetchall()

		timestamps = []
		for time in tupleTimestamps:
			# Take the list of tuples, turn them into datetime and make them into a less unwieldy list
			strToDatetime = datetime.datetime.strptime(time[0],'%d-%m-%Y')
			timestamps.append(strToDatetime)

		# Turn date to datetime
		date = datetime.datetime.strptime(date,'%d-%m-%Y')

		# Find the closest date in timestamps to the date provided in the function call
		newDate = min(timestamps, key=lambda sub: abs(sub - date))

		# Change back to a string
		date = newDate.strftime('%d-%m-%Y')

		# Retrieve data from the database with the new date.
		sqlCommand = "SELECT `ln_sponsored_stats`.`campaign_id`, `campaigns`.`campaign_name`, SUM(`cost`), SUM(`impressions`), SUM(`clicks`), SUM(`approx_unique_impressions`), SUM(`follows`), SUM(`page_clicks`), `timestamp` FROM `ln_sponsored_stats` INNER JOIN `campaigns` ON `ln_sponsored_stats`.`campaign_id`=`campaigns`.`campaign_id` WHERE `timestamp` = '"+date+"' GROUP BY `id`"
		db_cursor.execute(sqlCommand)
		fetchedStats = db_cursor.fetchall()

	# Close connection to the database.
	db.close()

	return fetchedStats

def getFollowerDemos(table, date):
	# ARGS
	# table = 	"Country",
	# 			"Industry",
	# 			"Job Function",
	# 			"Region",
	# 			"Seniority",
	# 			"Staff Count"
	# date = "dd-mm-yyyy"

	# dimension might be easier to use if it were a dict of dicts, but this works for the time being...
	dimension = {
		"Country":["follower_demos_country","country_id", "countries", "country", "country_urn" , "total_followers"],
		"Industry":["follower_demos_industry","industry_id", "industries", "industry_name", "industry_urn", "total_followers"],
		"Job Function":["follower_demos_job_function","function_id", "jobfunctions", "function_name", "function_urn", "total_followers"],
		"Region":["follower_demos_region","region_id", "regions", "region_name", "region_urn", "total_followers"],
		"Seniority":["follower_demos_seniority","seniority_id", "seniorities", "seniority_name", "seniority_urn", "total_followers"],
		"Staff Count":["follower_demos_staff_count","staffCountRange", "staff_counts", "staff_count_name", "staff_count_range", "total_followers"]}

	db = dbconnect()
	db_cursor = db.cursor()

	sqlCommand = "SELECT " + dimension[table][0] + "." + dimension[table][5] + ",  " + dimension[table][2] + "." + dimension[table][3] + ", " + dimension[table][0] + ".timestamp FROM " + dimension[table][0] + " INNER JOIN " + dimension[table][2] + " ON " + dimension[table][0] + "." + dimension[table][1] + " = " + dimension[table][2] + "." + dimension[table][4] + " WHERE " + dimension[table][0] + ".timestamp='" + date + "' ORDER BY " + dimension[table][0] + ".total_followers DESC LIMIT 10"

	db_cursor.execute(sqlCommand)
	results = db_cursor.fetchall()
	db.close()



	return results

def findHighestResult(key, date, offset=0):
	# Returns a string of the post text for the highest result of the dimension indicated in 'key' at the date indicated in 'date' (both input as strings)
	# 'key' can be any of the following: "impressions", "clicks", "CTR" or "shares"
	# 'offset' is an integer to get the post with the n'th highest result in 'key'
	# Note that 'offset' is 0-indexed
	# For example if you want to retrieve the post text for the post with the 3rd highest impressions on the 1st Jan 2021, you could use the following function call:
	# findHighestResult("impressions", "01-01-2021", 2)

	db = dbconnect()
	db_cursor = db.cursor()

	if key == "impressions":
		dimension = "impression_count"
	elif key == "clicks":
		dimension = "click_count"
	elif key == "CTR":
		dimension = "ctr"
	elif key == "shares":
		dimension = "share_count"


	sqlCommand = "SELECT `"+dimension+"`, posts.post_text FROM posts_stats INNER JOIN `posts` ON posts.post_id=`posts_stats`.id WHERE timestamp='"+date+"' ORDER BY `"+dimension+"` DESC LIMIT 1 OFFSET "+str(offset)+" "
	db_cursor.execute(sqlCommand)
	results = db_cursor.fetchall()
	db.close()

	return results

def uniqueVisitors(date):
	# Returns the number as a string of uniqueVisitors to the linkedin company page at the timestamp indicated by the 'timestamp' argument as a string in the format 'dd-mm-yyyy'
	db = dbconnect()
	db_cursor = db.cursor()

	sqlCommand = "SELECT SUM(`unique_page_views`) FROM page_stats WHERE timestamp >= '"+date+"'"
	db_cursor.execute(sqlCommand)
	results = db_cursor.fetchall()
	db.close()

	return results[0][0]

def getGoogle_Data(timestamp):
	# Returns data as a list of strings from the Google Ads Api at the timestamp indicated by the 'timestamp' argument as a string in the format 'dd-mm-yyyy'
	db = dbconnect()
	db_cursor = db.cursor()

	sqlCommand = "SELECT campaign_name, cost, impressions, clicks, conversions, campaign_status FROM google_spons WHERE timestamp='"+timestamp+"'"
	db_cursor.execute(sqlCommand)

	output = db_cursor.fetchall()
	db.close()
	return output
