import pyAesCrypt
import json
from werkzeug.security import check_password_hash
import os

def verify_password(username, password):
	with open("./encrypted_files/users.json") as json_file:
		users = json.load(json_file)
	if username in users and check_password_hash(users.get(username),password):
		pw = password
		return pw
	else:
		return False

def encryptFile(filename, username, password):
	if verify_password(username, password) != False:
		print("password correct")
		key = verify_password(username, password)
		pyAesCrypt.encryptFile(filename, filename+".aes", password)
		os.remove(filename)
		return 0
	else:
		print("incorrect password!")

def decryptFile(filename, username, password):
	inputFile = filename
	outputFile = filename[:-4]
	if verify_password(username, password) != False:
		print("Password Correct, decrypting : " + filename, flush=True)
		key = verify_password(username, password)
		print("key validated for: "+ filename, flush=True)
		pyAesCrypt.decryptFile(inputFile, outputFile, key)
		print(filename + " decrypted", flush=True)
		return
	else:
		print("Incorrect Password", flush=True)
		return print("Incorrect Password", flush=True)
