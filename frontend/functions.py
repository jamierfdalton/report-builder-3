# Misc useful functions
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import functions
import requests
import json
import db_functions as db

def endAtWhiteSpace(string, numberofwords):
	# Takes a sentence string as input and returns a string which ends at n'th word (given as 'numberofwords' - integer) in order that the returned string ends at a whole word.

	list = string.split(' ')
	newList =[]
	try:
		for x in range(numberofwords):
			newList.append(list[x])
	except:
		newList = list

	return ' '.join(newList)

def writeToFile(data, filename, writeorappend):
	# Writes data to new file given as a string in the data argument to the file given as a string in filename with the read/write permissions given as a string in writeorappend
	# writeorappend can take the arguments from python's read/write file function. e.g. "w+" or "w"
	data_file = filename
	f = open(data_file, writeorappend)
	f.write(data)
	f.close()

def sumOfLinkedInStats(listOfCampaigns):
	# Returns a list of common stats from linkedin organic campaigns
	# Takes a list of campaign IDs as strings as input (listOfCampagins).

	# TODO - Check if this can be replaced by a function from db_functions.

	# inititalise descriptive variables
	spend = 0
	impressions = 0
	clicks = 0
	cpc = 0
	reach = 0
	frequency = 0
	follows = 0
	clickstolinkedinpage = 0

	# Assign indexes to descriptive variables
	for x in listOfCampaigns:
		spend += x[2]
		impressions+= x[3]
		clicks+= x[4]
		reach+=x[5]
		follows+=x[6]
		clickstolinkedinpage+=x[7]
		date = x[8]

	# Calculate results that are derived from base statistics
	ctr = round(clicks/impressions*100,2)
	cpc = round((float(spend)/float(clicks)),2)
	frequency = round(impressions/reach,2)


	spend = "£" + str("{:,}".format(round(spend,2)))
	impressions = str("{:,}".format(impressions))
	clicks = str("{:,}".format(clicks))
	ctr = str(ctr)+"%"
	cpc = "£"+ str(cpc)
	reach = str("{:,}".format(reach))
	frequency = str("{:,}".format(frequency))
	follows = str("{:,}".format(follows))
	clickstolinkedinpage = str("{:,}".format(clickstolinkedinpage))

	output = [date, spend, impressions, clicks, ctr, cpc,reach, frequency, follows, clickstolinkedinpage]
	return output

def displayCampaignStats(TwoDimensionListOfCampaignData):
	listOfCampaigns = TwoDimensionListOfCampaignData

	tempList = []
	newList = []
	for x in listOfCampaigns:
		campaignName = x[1]
		spend = x[2]
		impressions= x[3]
		clicks= x[4]
		reach=x[5]
		ctr = round(clicks/impressions*100,2)
		cpc = round((float(spend)/float(clicks)),2)
		frequency = round(impressions/reach,2)

		tempList.append(campaignName)
		tempList.append("£" + str("{:,}".format(round(spend,2))))
		tempList.append(str("{:,}".format(impressions)))
		tempList.append(str("{:,}".format(clicks)))
		tempList.append(str(ctr)+"%")
		tempList.append("£"+ str(cpc))
		tempList.append(str("{:,}".format(reach)))
		tempList.append(str("{:,}".format(frequency)))
		newList.append(tempList)
		tempList = []

	return newList

def displayGoogleCampaignStats(TwoDimensionListOfCampaignData):
	listOfCampaigns = TwoDimensionListOfCampaignData
	#format of google output = campaign_name, cost, impressions, clicks, conversions, campaign_status

	tempList = []
	newList = []
	for x in listOfCampaigns:
		campaignName = x[0]
		cost = x[1]
		impressions= x[2]
		clicks= x[3]
		conversions=x[4]
		ctr = round(clicks/impressions*100,2)
		cpc = round((float(cost)/float(clicks)),2)
		campaignStatus = x[5]
		if conversions != 0:
			costPerConversion = round((float(cost)/float(conversions)),2)
		else:
			costPerConversion = 0.00

		tempList.append(campaignName)
		tempList.append("£" + str("{:,}".format(round(cost,2))))
		tempList.append(str("{:,}".format(impressions)))
		tempList.append(str("{:,}".format(clicks)))
		tempList.append(str(ctr)+"%")
		tempList.append("£"+ str(cpc))
		tempList.append(str("{:,}".format(conversions)))
		tempList.append("£"+ str("{:,}".format(round(costPerConversion,2))))
		tempList.append(campaignStatus)
		newList.append(tempList)
		tempList = []

	return newList

def combineLastWeeksDataWithToday(currentDataFile, previousDataFile, dimension):
    with open(config.datafiles + currentDataFile) as json_file:
        currentData = json.load(json_file)

    with open (config.datafiles + previousDataFile) as json_file:
        lastData = json.load(json_file)

    try:
        for sizeRanges in lastData:
            sizeRanges['staffCountRange'] = sizeRanges['staffCountRange'].capitalize()[5:].replace("_"," ")
    except:
        pass

    i = 0
    while i < 10 and i < len(lastData):
        k = 0
        while k < len(lastData):
            if currentData[i][dimension] == lastData[k][dimension]:
                currentData[i]['lastWeeksFollowerCount'] = lastData[k]['totalFollowerCount']
            k += 1
        i += 1
    newJson = json.dumps(currentData, indent = 2)
    filename = config.datafiles + currentDataFile
    writeToFile(newJson, filename, 'w+')
    return filename

def createFollowerGraphs(dimension):
	# dimension must be either follower_demos_country, follower_demos_industry, follower_demos_job_function, follower_demos_region, follower_demos_seniority or follower_demos_staff_count

	r = requests.get('http://config:5000/api/getconfig')
	config = json.loads(r.text)

	f = open("config.json", "w")
	f.write(r.text)
	f.close()
	f = open("config.json", "r")
	f.close()

	date = config['dateSettings']['todayddmmyy']

	names = []
	followerCounts = []

	data = db.getFollowerDemos(dimension, date)

	for row in data:
		followerCounts.append(row[0])
		names.append(row[1])

	# # create the matplotlib figure and all its styling
	#
	# # figure appears to need to come before you actually create the barh otherwise it overwrites the data. I don't know why (yet)
	# # This sets the size in inches and dpi of the image.
	plt.figure(num=None, figsize=(6,2), dpi=100, edgecolor='w')
	fig = plt.gcf()
	fig.subplots_adjust(left=0.40, right= 1)

	params = {'ytick.labelsize': 9,'xtick.labelsize': 9,'axes.titlelocation': 'left', 'axes.titlesize': 14, 'axes.linewidth': 0}
	plt.rcParams.update(params)

	# # This creates the barh using the data from the lists above.
	bargraph = plt.barh(names,followerCounts)
	plt.gca().invert_yaxis()

	# This creates the title.
	plt.title("Top Followers by "+ dimension)

	# This saves the file and then clears the data so the next time we call this function it doesn't include the data from the previous call.
	plt.savefig("./static/images/"+ str(dimension) + '.png')
	print(dimension + " graph created")
	plt.clf()
	plt.cla()
	plt.close()
	f.close()


def createMultiSeriesFollowerGraphs(inputFilenameCurrent, inputFilenameLast, dimension, title):
    # dimension must be either 'region', 'industry', 'function', 'countryName', 'seniority', 'staffCountRange'
    filename = combineLastWeeksDataWithToday(inputFilenameCurrent, inputFilenameLast, dimension)

    with open(filename) as json_file:
        richNamesCurrent = json.load(json_file)

    # Get top ten values for use as data for current report
    i = 9
    labelsList = []
    while i >= 0:
        try:
            labelsList.append(richNamesCurrent[i][str(dimension)])
        except:
            pass
        i -= 1

    labels = tuple(labelsList)

    k = 9
    followerCountsCurrent = []
    while k >= 0:
        try:
            followerCountsCurrent.append(richNamesCurrent[k]['totalFollowerCount'])
        except:
            pass
        k -= 1

    j = 9
    followerCountsLast = []
    while j >= 0:
        try:
            followerCountsLast.append(richNamesCurrent[j]['lastWeeksFollowerCount'])
        except:
            pass
        j -= 1

    params = { 'font.size' : 20, 'axes.titlelocation': 'left','axes.titleweight': 'bold', }
    plt.rcParams.update(params)

    x = np.arange(len(labels))  # the label locations
    height = 0.35  # the height of the bars

    fig, ax = plt.subplots(figsize=(16.03, 5.34), dpi=100, edgecolor='w')

    rects1 = ax.barh(x + height/2, followerCountsCurrent, height, label='Current')
    rects2 = ax.barh(x - height/2, followerCountsLast, height, label='Last Report')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_title('Followers by ' + title)
    ax.set_yticks(x)
    ax.set_yticklabels(labels)
    ax.legend()
    fig.subplots_adjust(left=0.35, right = 0.9)

    # # This saves the file and then clears the data so the next time we call this function it doesn't include the data from the previous call.
    plt.savefig(config.images + 'followersby'+ str(dimension) + '.png')
    print("followers by " + str(title) +" created")
    plt.clf()
    plt.cla()
    plt.close()

    return richNamesCurrent
