import getGoogleAdsReport
import getLinkedInReport
import requests
import os, json

def getconfig():
    r = requests.get('http://config:5000//api/getconfig' , auth=("flagship", "fl48h1p"))
    f = open("config.json", "w")
    f.write(r.text)
    f.close()
    f = open("config.json", "r")
    f.close()

def cleanup():
    os.listdir()
    os.listdir('/code/data')
    f = open("/code/encrypted_files/secrets.json" , "w")
    f.write("0000")
    f.close()

    f = open("/code/encrypted_files/google-ads.yaml", "w")
    f.write("0000")
    f.close()

    f = open("/code/encrypted_files/linkedin_access_token.txt", "w")
    f.write("0000")
    f.close()
    os.remove("config.json")

def googleAdsReport(id):
    getGoogleAdsReport.main(id)
    # create custom error handling here.

def linkedinAdsReport():
    getLinkedInReport.main()

def main():
    print("getting config")
    getconfig()
    print("opening config")
    f = open("config.json", "r")
    config = json.loads(f.read())
    print("importing db functions")
    import db_functions as db
    print("getting linkedin ads report")
    linkedinAdsReport()
    print("updating db")
    db.update()
    db.closeConnection()
    print("end!")

main()
