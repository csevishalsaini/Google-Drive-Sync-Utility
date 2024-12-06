import os
from googleapiclient.http import MediaFileUpload
import json
from load_config import loadConfig
from googleapiclient.errors import HttpError


# GLOBAL VARIABLES
base_path = None
ignore_config = loadConfig('ignore_config')

def existsInDrive(service, ftype, fname, parent):
	query = ''
	if ftype == 'file':
		query = "name = '{}' and mimeType != 'application/vnd.google-apps.folder' and '{}' in parents and trashed = false".format(fname, parent)
	elif ftype == 'folder':
		query = "name = '{}' and mimeType = 'application/vnd.google-apps.folder' and '{}' in parents and trashed = false".format(fname, parent)
	else:
		print["[ERROR] searching for invalid file type"]
		return -1

	try:
		response = service.files().list(q=query,
										spaces='drive',
										fields='files(id, name, trashed, parents)'
									).execute()

		# print(response.get('files', []))
		# for file in response.get('files', []):
		# 	print(file.get('id'), file.get('name'), file.get('trashed'))

		if len(response.get('files', [])) > 0:
			return response.get('files', [])[0].get('id')
		else:
			return -1
	
	
	except HttpError:
		print("[ERROR] {} {} doesn't exist".format(ftype, fname))
		return -1


def uploadFolder(service, local_entry, target_folder_id):
	# set base path
    if base_path == None:
        base_path = local_entry
    print("\n[LOC] "+ local_entry.replace(base_path, '~/'))
	# print('target_folder_id: ', target_folder_id)
	for item in sorted(os.listdir(local_entry)):
		item_path = os.path.join(local_entry, item)

		# item type
		ftype = ''
		if os.path.islink(item_path):
			ftype = 'link'
		if os.path.isdir(item_path):
			ftype = 'folder'
		elif os.path.isfile(item_path):
			ftype = 'file'

		# check for ignore
		if item in ignore_config["ignore-files"]:
			print('[IGNORE] '+ str(item))
			continue
		if ftype == 'file' and item.find('.') != -1 and item.split('.')[-1] in ignore_config["ignore-extensions"]:
			print('[IGNORE] '+ str(item))
			continue

		# check for already exist
		if ftype == 'file' and existsInDrive(service, ftype, item, target_folder_id) != -1:
			print('[SKIP] {}: {}'.format(ftype, item))
			continue


		# if folder
		if ftype == 'folder':
			# check if folder already exists in gDrive
			exists = existsInDrive(service, ftype, item, target_folder_id)
			if exists != -1:
				print('[SKIP] create {}: {}'.format(ftype, item))
				uploadFolder(service, item_path, exists)
			else:
				# create folder
				file_metadata = {
					'name': item,
					'mimeType': 'application/vnd.google-apps.folder',
					'parents': [target_folder_id]
				}
				folder = service.files().create(body=file_metadata, fields='id, name').execute()
				folder_id = folder.get('id')
				folder_name = folder.get('name')
				print('[CREATE] folder: %s' % folder_name)
				uploadFolder(service, item_path, folder_id)


		# if file
		elif ftype == 'file':
			file_metadata = {
							'name': item,
							'parents': [target_folder_id]
			}
			media = MediaFileUpload(item_path, resumable=True)
			file = service.files().create(body=file_metadata,
												media_body=media,
												fields='id, name').execute()
			print('[UPLOAD] file: %s' % file.get('name'))

		elif ftype == 'link':
			print('*[SKIP] link: '+ str(item))

		else:
			print('*[SKIP] unknown: '+ str(item))


