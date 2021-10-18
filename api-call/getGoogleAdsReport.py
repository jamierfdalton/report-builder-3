import sys
from datetime import timedelta, datetime
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import yaml, json
import os

def queryGoogle(client, customer_id):
    print("Querying Google", flush=True)
    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT campaign.serving_status, campaign.id, campaign.name, metrics.cost_micros, metrics.impressions,
        metrics.clicks, metrics.ctr, metrics.average_cpc, metrics.conversions, metrics.cost_per_conversion
        FROM campaign
        ORDER BY campaign.id"""

    print("Getting response", flush=True)
    response = ga_service.search_stream(customer_id=customer_id, query=query)

    costTotal = 0
    impressionsTotal = 0
    clicksTotal = 0
    CTR = 0
    avgCPC = 0
    conversionsTotal = 0
    CPL = 0

    output = []
    temp = []
    for batch in response:
        for row in batch.results:
            costTotal += row.metrics.cost_micros/1000000
            impressionsTotal += row.metrics.impressions
            clicksTotal += row.metrics.clicks
            conversionsTotal += row.metrics.conversions

            campaignStatus = str(row.campaign.serving_status)
            allCampName = row.campaign.name
            allCampCost = row.metrics.cost_micros/1000000
            allCampImps = row.metrics.impressions
            allCampClicks = row.metrics.clicks
            allCampCTR = row.metrics.ctr * 100
            allCampCPC = row.metrics.average_cpc/1000000
            allCampConv = row.metrics.conversions
            allCampCPL = row.metrics.cost_per_conversion/1000000

            temp.append(campaignStatus[22:])
            temp.append(str(allCampName))
            temp.append("£"+"{:,}".format(round(allCampCost, 2)))
            temp.append("{:,}".format(allCampImps))
            temp.append("{:,}".format(allCampClicks))
            temp.append(str(round(allCampCTR, 2)) + "%")
            temp.append("£"+ str(round(allCampCPC, 2)))
            temp.append("{:,}".format(int(allCampConv)))
            temp.append("£"+ str(round(allCampCPL, 2)))
            output.append(temp)
            temp = []

    return output

def previous_report(client, customer_id, daysInPast):
    ga_service = client.get_service("GoogleAdsService")

    today = datetime.now()
    timeDelta = timedelta(days = daysInPast)
    previousTime = today - timeDelta

    startdate = "'1999-01-01'"
    enddate =  "'" + str(previousTime.strftime('%Y-%m-%d'))+ "'"

    query = """
    SELECT campaign.id, campaign.name, metrics.cost_micros, metrics.impressions,
    metrics.clicks, metrics.ctr, metrics.average_cpc, metrics.conversions, metrics.cost_per_conversion
    FROM campaign
    WHERE segments.date BETWEEN {} AND {}
    ORDER BY campaign.id""".format(startdate, enddate)

    # Issues a search request using streaming.
    response = ga_service.search_stream(customer_id=customer_id, query=query)

    costTotal = 0
    impressionsTotal = 0
    clicksTotal = 0
    CTR = 0
    avgCPC = 0
    conversionsTotal = 0
    CPL = 0

    output = []
    temp = []
    for batch in response:
        for row in batch.results:
            costTotal += row.metrics.cost_micros/1000000
            impressionsTotal += row.metrics.impressions
            clicksTotal += row.metrics.clicks
            conversionsTotal += row.metrics.conversions

            campaignStatus = str(row.campaign.serving_status)
            allCampName = row.campaign.name
            allCampCost = row.metrics.cost_micros/1000000
            allCampImps = row.metrics.impressions
            allCampClicks = row.metrics.clicks
            allCampCTR = row.metrics.ctr * 100
            allCampCPC = row.metrics.average_cpc/1000000
            allCampConv = row.metrics.conversions
            allCampCPL = row.metrics.cost_per_conversion/1000000

            temp.append(campaignStatus[22:])
            temp.append(str(allCampName))
            temp.append("£"+"{:,}".format(round(allCampCost, 2)))
            temp.append("{:,}".format(allCampImps))
            temp.append("{:,}".format(allCampClicks))
            temp.append(str(round(allCampCTR, 2)) + "%")
            temp.append("£"+ str(round(allCampCPC, 2)))
            temp.append("{:,}".format(int(allCampConv)))
            temp.append("£"+ str(round(allCampCPL, 2)))
            output.append(temp)
            temp = []

    return output

def main(googleAdsCustomerId):
    data_file = '/code/data/google_data.json'
    with open (data_file, "w+") as file:
        print('google_data.json file opened')
        ## If it fails at this point, remove the apps access from your google account and get a new access token.
        google_ads_client = GoogleAdsClient.load_from_storage("/code/encrypted_files/google-ads.yaml")
        print('googleAdsClient loaded from storage')

        total = []
        current = queryGoogle(google_ads_client, str(googleAdsCustomerId))
        print('current stats queried')
        previous = previous_report(google_ads_client, googleAdsCustomerId, 14)
        print('prvious 14 days stats queried')
        total.append(current)
        print('Current data appended to total')
        total.append(previous)
        print('previous data appended to total')
        output = json.dump(total, file, ensure_ascii=False)
        print('json dumped')
    return 0
