import getLinkedInReport as glr
import json

import requests

### This is a temporary skeleton for implementing a real login system in future, so we're not worried about the
### Security implications of a plain-text password.
r = requests.get('http://config:5000/api/getconfig', auth=("flagship", "fl48h1p"))
config = json.loads(r.text)

f = open("./encrypted_files/config.json", "w+")
f.write(r.text)
f.close()
f = open("./encrypted_files/config.json", "r")
f.close()

import db_functions as db

print(glr.getSharesByOrg())
