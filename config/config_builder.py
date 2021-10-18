from datetime import datetime, timedelta
import os
import settings
import json

output = {
    "directories":{
        "images": "/code/static/images/",
        "logs": "/code/logs",
        "databaseName":""
    },
    "companyIDs":{
      "companyURN":"",
      "companyName": ""
    },
    "campaignIDs":{
        "campaignNumbers":[],
        "campaignURNs":[]
    },
    "sponsoredAccountURN":"",
    "dateSettings":{
        "todayddmmyy":"",
        "lastWeekDateTime":"",
        "lastFortnightDateTime":"",
        "lastFortnightDateTimeddmmyyyy":"",
        "timeDeltaDaysPast":"",
        "timeDeltaDaysPastYYYYMMDD":"",
        "currentHourMinus30Days":"",
        "sponsoredStartDate":"",
        "organicStartDate":"",
        "dayInMs":"86400000"
        },
    "google":{
        "googleAdsCustomerId":""
    },
    "linkedin":{
        "datafiles": "/code/data/",
        "logs": "/code/logs/",
    },

    }

def buildConfig():
    ## Paths
    # Needs to be the result of user input
    output["directories"]["databaseName"] = "report-builder"

    ## Company Ids
    # Needs to be the result of user input
    output["companyIDs"]["companyURN"] = 'urn:li:organization:' + settings.companyNumber
    output["companyIDs"]["companyName"] = settings.companyName

    campaignNumbers = []
    for i in settings.campaignNumber:
        campaignNumbers.append(i)
    output["campaignIDs"]["campaignNumbers"] = campaignNumbers

    campaignURNs = []
    for i in settings.campaignNumber:
        campaignURNs.append('urn:li:sponsoredCampaign:' + str(i))

    output["campaignIDs"]["campaignURNs"] = campaignURNs

    output["sponsoredAccountURN"] = 'urn:li:sponsoredAccount:'+ settings.advertisingID


    ## Time and Date variables
    today = datetime.now()
    timeDeltaInDays = 30
    currentHour = str(int(datetime.timestamp(today)/60/60))
    lastFortnightDateTime = datetime.now() - timedelta(days = 14)
    timeDeltaDaysPast = datetime.now() - timedelta(days = timeDeltaInDays)
    output["dateSettings"]["todayddmmyy"] = today.strftime('%d-%m-%Y')
    output["dateSettings"]["timeDeltaInDays"] = timeDeltaInDays
    output["dateSettings"]["currentHour"] = currentHour
    output["dateSettings"]["hourInMs"] = 3600000
    output["dateSettings"]["dayInMs"] = 86400000
    output["dateSettings"]["lastFortnightDateTimeddmmyyyy"] = lastFortnightDateTime.strftime('%d-%m-%Y')
    output["dateSettings"]["timeDeltaDaysPastYYYYMMDD"] = timeDeltaDaysPast.strftime('%Y-%m-%d')
    output["dateSettings"]["currentHourMinus30Days"] = int(currentHour) - 720
    output["dateSettings"]["sponsoredStartDate"] = settings.sponsoredStartDate
    output["dateSettings"]["organicStartDate"] = settings.organicStartDate

    output["google"]["googleAdsCustomerId"] = '2978660145'


    jsonOutput = json.dumps(output, indent = 2)
    print("config built", flush=True)

    return jsonOutput
