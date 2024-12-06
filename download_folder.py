import os
from googleapiclient.http import MediaIoBaseDownload
import json
from load_config import loadConfig
from googleapiclient.errors import HttpError
from upload_folder import existsInDrive
import io

# GLOBAL VARIABLES
base_path = None

def DownloadFile(service, file_id, file_name, save_to):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("[DOWNLOAD] {} {}%.".format(file_name, int(status.progress()*100)))

    file_name = os.path.join(save_to, file_name)
    with open(file_name, 'wb') as f:
        f.write(fh.getvalue())


def existsOnLocal(file_path):
    return os.path.exists(file_path)



def downloadFolder(service, local_entry, source_folder_id):
    # set base path
    if base_path == None:
        base_path = local_entry
    print("\n[LOC] "+ local_entry.replace(base_path, '~/'))

    # Download Files
    query = "mimeType != 'application/vnd.google-apps.folder' and '{}' in parents and trashed = false".format(source_folder_id)

    try:
        response = service.files().list(q=query,
                                        spaces='drive',
                                        fields='files(id, name, trashed, parents)'
                                    ).execute()

        # print(response.get('files', []))
        for file in response.get('files', []):
            # print(file.get('id'), file.get('name'), file.get('trashed'))
            f_id = file.get('id')
            f_name = file.get('name')
            if existsOnLocal(os.path.join(local_entry, f_name)):
                print('[SKIP] {}'.format(f_name))
                continue
            else:
                DownloadFile(service, file.get('id'), file.get('name'), local_entry)
            

    except HttpError:
        print('[ERROR] no files found on gDrive')


    # Download Folders
    query = "mimeType = 'application/vnd.google-apps.folder' and '{}' in parents and trashed = false".format(source_folder_id)

    try:
        response = service.files().list(q=query,
                                        spaces='drive',
                                        fields='files(id, name, trashed, parents)'
                                    ).execute()

        # print(response.get('files', []))
        for file in response.get('files', []):
            # print(file.get('id'), file.get('name'), file.get('trashed'))
            f_id = file.get('id')
            f_name = file.get('name')
            f_path = os.path.join(local_entry, f_name)
            if existsOnLocal(f_path):
                print('[SKIP] folder: {}'.format(f_name))
            else:
                print('[CREATE] folder: %s' % f_name)
                os.mkdir(f_path)
            # Recursive
            downloadFolder(service, f_path, f_id)
            
    except HttpError:
        print('[ERROR] no files found on gDrive')