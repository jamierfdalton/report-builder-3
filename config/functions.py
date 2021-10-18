from datetime import datetime as dtfunctiofunctions.verify_password()ns.verify_password()
import json

def datetimeToMs(dt):
	return int(dt.timestamp()*1000)

def writeToFile(data, filename, writeorappend):
	data_file = filename
	f = open(data_file, writeorappend)
	f.write(data)
	f.close()

def currentTimeMinusTimeDeltaInMs():
	with open("config.json", "r") as file:
		config = json.loads(file.read())

	return datetimeToMs(dt.today()) - (config['dateSettings']['dayInMs'] * config['dateSettings']['timeDeltaInDays'])

def sponsoredStartdate():
	with open("config.json", "r") as file:
		config = json.loads(file.read())
	return msToDatetime(int(config['dateSettings']['sponsoredStartDate']))

def currentTimeMinusTimeDeltaInDatetime():
	return msToDatetime(currentTimeMinusTimeDeltaInMs())

def datetimeToMs(dt):
	return int(dt.timestamp()*1000)

def msToDatetime(timestampInMs):
	return dt.fromtimestamp(timestampInMs/1000)
