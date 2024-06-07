import requests, logging, argparse

logger = logging.getLogger(__name__)

class gofile:
    api_base_domain = 'https://api.gofile.io/'
    server_base_domain=r"https://{server}.gofile.io/"
    base_domain = "https://gofile.io/api"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"

    def __init__(self, token=None):
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': gofile.user_agent})
        _=self.get_server()

    def upload_files(self,files_to_upload,folder_name=None):
        if len(files_to_upload) < 2:
            json_data = self.single_upload(files_to_upload[0])
            url = json_data['data']['downloadPage']
            folder_id = json_data['data']['parentFolder']
            if not self.token:
                self.token=json_data['data']['guestToken']
         
        else:
            url , folder_id = self.multiple_upload(files_to_upload)

        if folder_name:
            self.update_folder(folder_id,{'name':folder_name})

        return url
    
    def multiple_upload(self,files_to_upload):
        number_of_files = len(files_to_upload)
        logger.info(f"uploading file {1:>{len(str(number_of_files))}}/{number_of_files}: '{files_to_upload[0]}'")
        try:
            json_data = self.single_upload(files_to_upload[0])
            token=self.token if self.token else json_data['data']['guestToken']
            folder_id=json_data['data']['parentFolder']
        except Exception as e:
            logger.error(f"initial upload failed, aborting - {e}")
            return None
        self.token=token
        options = {
                'token': token,
                'folderId': folder_id
            }
        
        for index,file in enumerate(files_to_upload[1:]):
            logger.info(f"uploading file {index+2:>{len(str(number_of_files))}}/{number_of_files}: '{file}'")
            self.single_upload(file, options)
        
        return json_data['data']['downloadPage'], folder_id

    def single_upload(self,file, data=None):
        files = {'file': open(file, 'rb')}
        response = self.session.post(
            self.server_url+'uploadFile',
            files=files,
            data=data
        )
        if  response.status_code == 200:
            logger.info({'success': True,'name': response.json()['data']['fileName'],'url':response.json()['data']['downloadPage']})

        else:
            logger.error(f'upload of {file} failed - HTTP_error_code: {response.status_code}')
            logger.debug(response.text)
            return None
        
        return response.json()

    def get_server_url(self):
        _=self.get_server()
        self.server_url=gofile.server_base_domain.replace('{server}',self.server)
        return self.server_url
    
    def update_folder(self,folder_id,data):
        headers= {
            'Authorization': f'Bearer {self.token}'
        }
        self.session.headers.update(headers)
        for key, value in data.items():
            logger.info(f"updating album property '{key}' to '{value}'")
            options ={"attribute":key, "attributeValue":value}
            try:
                response = self.session.put(
                    gofile.api_base_domain + f'contents/{folder_id}/update',
                    json=options
                )
                if  response.status_code == 200:
                    logger.info(response.text)

                else:
                    logger.error(response.text)

            except Exception as e:
                logger.error(response.text)


    def get_server(self, return_url=True):
        r = self.session.get(gofile.api_base_domain + 'getServer' )
        self.server=r.json()['data']['server']
        self.server_url=gofile.server_base_domain.replace('{server}',self.server)
        if return_url:
            return self.server_url
        return self.server


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
    description='Example: gofile <file/folder_path>')
    parser.add_argument(
        '-i',
        '--individual-links',
        help=
        'Upload multiple files individually, without creating an album, generating one link per file. Ignores -n',
        action='store_true')
    parser.add_argument('-vv',
                        '--verbose',
                        help='Show more information',
                        action='store_true')
    parser.add_argument('path',
                        nargs='+',
                        help='Path to the file(s) and/or folder(s)')
    parser.add_argument(
        '-n',
        '--album_name', dest='album_name',
        help=
        'Album nameto use')
    parser.add_argument(
        '-T',
        '--api_token', dest='token_file', default=None,
        help=
        'Path to file containing your API_TOKEN (plain text)')
    parser.add_argument(
        '-t',
        '--token', dest='token', default=None,
        help=
        'Your gofile API_TOKEN')
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    if not args.token:
        logger.info('using anonymus mode (ano API_TOKEN provided)')
    gofile_conn=gofile(args.token)
    logger.error('stand along use not implemented yet')