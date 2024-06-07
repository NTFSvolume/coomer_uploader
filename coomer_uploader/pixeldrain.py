import requests, logging, mimetypes, argparse

from pathlib import Path
import base64

logger = logging.getLogger(__name__)

class pixeldrain:
    api_base_domain ='https://pixeldrain.com/' 
    base_domain = 'https://pixeldrain.com/'
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"

    def __init__(self, api_key=None):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': pixeldrain.user_agent})

    def upload_files(self, files_to_upload, album_name=None):
        number_of_files = len(files_to_upload)
        ids = []
        if self.api_key:
            headers = {
                "Authorization": "Basic " + base64.b64encode(f":{self.api_key}".encode()).decode(),
            }
        else:
            headers = {}

        self.session.headers.update(headers)
        

        for index,file in enumerate(sorted(files_to_upload)):
            logger.info(f"uploading file {index+1:>{len(str(number_of_files))}}/{number_of_files}: '{file}'")
            mimetype, _ = mimetypes.guess_type(file) 
            logger.debug(f"MIME type for {file} is: {mimetype}")

            self.session.headers.update({'Content-Type':mimetype})

            files = {'file': open(file, 'rb')}

            data = {
                "name": Path(file).name,
                "anonymous": False if self.api_key else True
            }
            
            response = self.session.put(
                pixeldrain.api_base_domain+f'api/file/{Path(file).name}',
                data=data, files=files
                #auth=("u", self.api_token) if self.api_token else None
            )

            if  response.status_code == 201:
                id = response.json()['id']
                logger.info({'success': True, 'name': response.json()['name'],'id':response.json()['id']})
                ids.append(id)

            else:
                logger.error(f'upload of {file} failed - HTTP_error_code: {response.status_code}')
                logger.info(response.text)
                continue

        if len(ids)==0:
            return None
        return self.create_album(ids,album_name)

    def create_album(self,ids, album_name):        
        json_data = {
            'title': album_name,
            "anonymous": False if self.api_key else True, 
            'files': [{'id': id} for id in ids]
            }
        
        response = requests.post(pixeldrain.api_base_domain+'api/list', json=json_data)
        if  response.status_code != 201:
            logger.error(f"creation of album '{album_name}' failed - HTTP_error_code: {response.status_code}")
            return None
        id = response.json()['id']
        logger.info(f"album created {{'name': '{album_name}', 'id': '{id}'}}")
        return pixeldrain.base_domain + f'l/{id}'

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
    description='Example: pixeldrain <file/folder_path>')
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
        'Album name to use')
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
    gofile_conn=pixeldrain(args.token)
    logger.error('stand along use not implemented yet')