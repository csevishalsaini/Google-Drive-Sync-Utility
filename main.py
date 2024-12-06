# https://developers.google.com/drive/api/v3/quickstart/python
# installation modules
# pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

from __future__ import print_function
import pickle
import os.path
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from load_config import loadConfig
from upload_folder import uploadFolder
from download_folder import downloadFolder
from developer_intro import developerIntro


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
	"""Shows basic usage of the Drive v3 API.
	Prints the names and ids of the first 10 files the user has access to.
	"""
	creds = None
	# The file token.pickle stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	if os.path.exists('token.pickle'):
		with open('token.pickle', 'rb') as token:
			creds = pickle.load(token)

	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json', SCOPES)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open('token.pickle', 'wb') as token:
			pickle.dump(creds, token)

	service = build('drive', 'v3', credentials=creds)
	




	# Load Local Configurations
	local_config = loadConfig('local_config')
	# Developer Intro
	developerIntro("who.is.vikas")
	# Upload New Folders and Files
	print('======================================================================')
	print('                           UPLOAD HANDLER                             ')
	print('======================================================================')
	uploadFolder(service, local_config['local-entry'], local_config['gDrive-entry'])
	# Download Old Folders and Files
	print('======================================================================')
	print('                          DOWNLOAD HANDLER                            ')
	print('======================================================================')
	downloadFolder(service, local_config['local-entry'], local_config['gDrive-entry'])
	print('======================================================================')
	print('                              SYNQ OVER                               ')
	print('======================================================================')




if __name__ == '__main__':
	main()