from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials
from apiclient import errors
from apiclient import http
from pathlib import Path

class gdrive:

    def __init__(self, _drive=None):
        self.drive = self.connect_gdrive() if _drive is None else _drive
        self.root_dir_id = 'root'
        self.cur_dir_id = 'root'
        self.recent_result_dict = None

        # Todo: print intermediate results
        self.print_result = False
        

    @staticmethod
    def connect_gdrive():
        # Authenticate with Google
        auth.authenticate_user()
        gauth = GoogleAuth()
        gauth.credentials = GoogleCredentials.get_application_default()
        drive = GoogleDrive(gauth)
        return drive

    def upload_to_gdrive(self, src_fpath, dst_dir_id=None):
        dst_dir_id = dst_dir_id if dst_dir_id is not None else self.cur_dir_id
        f = self.drive.CreateFile({'parents': [{'id': dst_dir_id}]})
        f.SetContentFile(src_fpath)
        f.Upload()
        print('uploaded: title: %s, id: %s' % (f['title'], f['id']))
        
    def parent_dir(self, dir_id=None):
        dir_id = dir_id if dir_id is not None else self.cur_dir_id
        f = self.drive.CreateFile({'id': dir_id})
        return f['parents']

    def parent_dir_id(self, dir_id=None):
        dir_id = dir_id if dir_id is not None else self.cur_dir_id
        parent_dict = self.parent_dir(dir_id)
        return parent_dict[0]['id']

    def cd_root(self):
        self.cur_dir_id = self.root_dir_id
    
    def cd_parent(self):
        self.cur_dir_id = self.parent_dir_id()

    def cd_dir_id(self, dir_id):
        self.cur_dir_id = dir_id

    def cd_path(self, path):
        dst_path = Path(path)
        parts = list(dst_path.parts)

        for p in parts:
            if p == 'root':
                self.cd_root()
                continue
            ls_result = self.ls(print_result=False)

            title_list = [i['title'] for i in ls_result['folder_list']]
            try:

                index_found = title_list.index(p)
            except:
                print('%s cannot found in :' %p)
                print(title_list)
                break

            id_found = ls_result['folder_list'][index_found]['id']
            self.cd_dir_id(id_found)


    def ls(self, dir_id=None, print_result=True):
        dir_id = self.cur_dir_id if dir_id is None else dir_id
        
        folder_list = self.drive.ListFile({'q': "'%s' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"%dir_id}).GetList()
        file_list = self.drive.ListFile({'q': "'%s' in parents and mimeType!='application/vnd.google-apps.folder' and trashed=false"%dir_id}).GetList()
        
        if print_result:
            print('#folders#')
            for f in folder_list:
                print('%-25s \tid: %s' % (f['title'], f['id']))
            print('\n#files#')
            for f in file_list:
                print('%-25s \tid: %-50s \t type: %s' %
                      ( f['title'], f['id'], f['mimeType']))

            print('\n'*3)

        result_dict = {'folder_list':folder_list, 'file_list':file_list}
        self.recent_result_dict = result_dict
        return result_dict
    
    def download_file(self, src_id, dst_path, mk_dir=True):
        # Download a file from google drive to kernel 
        dst_path = Path(dst_path)
        if mk_dir:
            dst_path.mkdir(parents=True, exist_ok=True)
        # Initialize GoogleDriveFile instance with file id.
        download_file = self.drive.CreateFile({'id': src_id})
        download_file.GetContentFile(dst_path / download_file['title'])
        

    def fetch_meta(self, id):
        f = self.drive.CreateFile({'id': src_id})
        return f.FetchMetadata()


    def download_files_in_dir(self, src_dir_id, dst_path, mk_dir=True):
        # Download all files in src_id(directory in gdrive)
        ls_result = self.ls(src_dir_id, print_result='False')
        dst_path = Path(dst_path)
        for f in ls_result['file_list']:
            download_file = self.drive.CreateFile({'id': f['id']})
            download_file.GetContentFile(dst_path / download_file['title'])
            print('title: %s, id: %s' % (f['title'], f['id']))


    def download_dir(self, src_id, dst_path, recursive=False):
        # Download a folder from google drive to kernel 
        pass

    def upload_file(self, src_path, dst_id=None):
        # Upload a file from kernel drive to google drive 
        # dst_id should be a directory id
        dst_id = self.cur_dir_id if dst_id is None else dst_id
        src_path = Path(src_path)
        file1 = self.drive.CreateFile({'title': src_path.name, 'parents':[{'id':dst_id}]})
        file1.SetContentFile(str(src_path))
        file1.Upload() # Upload the file.
        print('title: %s, id: %s' % (file1['title'], file1['id']))

    def upload_dir(self, src_path, dst_id):
        # Upload a file from kernel drive to google drive 
        pass
