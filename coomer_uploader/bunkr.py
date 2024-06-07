import requests, json, logging, mimetypes, argparse

logger = logging.getLogger(__name__)

class bunkr:
    api_base_domain = 'https://app.bunkr.si/'
    base_domain = "https://bunkr.si/a/"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
    
    def __init__(self, token, cookies =None, cookies_file=None):
        self.token = token
        self.cookies= cookies 
        self.cookies_file= cookies_file
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': bunkr.user_agent})
        if self.cookies_file:
            self.read_cookies_from_file(self.cookies_file)

    def get_albums(self):
        r = self.session.get(
            bunkr.api_base_domain+'api/albums/edit',
            headers={ 'token': self.token},
        )
        
        if  r.status_code != 200:
            logger.error(f"unable to get album list - HTTP_error_code: {r.status_code}")
            return None

        return r.json()['albums']

    def get_album_url(self, album_id=None):
        albums = self.get_albums()
        for album in albums:
            if album.get('id') == album_id :
                return bunkr.base_domain +album.get('identifier')
        return None
        
    def create_album(self, album_name, description= "", public=True, download= True):
        json_data = {
                'name': album_name,
                'description': description,
                'download': download,
                'public': public
            }
            
        
        response = self.session.post(
            bunkr.api_base_domain+'api/albums',
            headers={'token': self.token},
            json=json_data
        )
        if  response.status_code == 200:
            id = response.json()['id']
            logger.info(f"album created {{'name': '{album_name}', 'id': '{id}'}}")
        else:
            raise ValueError(f"unable to create album '{album_name}' - {response.json()['description']}")
    
        return id

    def get_api_server(self):
        r = self.session.get(bunkr.api_base_domain+'api/node', headers={'token': self.token})
        if  r.status_code != 200:
            logger.error(f'unable to get api url - HTTP_error_code: {r.status_code}')
            return None
        return r.json()['url']

    def upload_files(self, files_to_upload, album_name=None):
        try:
            album_id = self.create_album(album_name)
            album_url=self.get_album_url(album_id)
            server = self.get_api_server()
        except Exception as e:
            logger.error(f'unable to prepare upload - {e}')
            return None
        
        logger.info(f'uploading files to {album_url}')
        number_of_files = len(files_to_upload)

        for index,file in enumerate(sorted(files_to_upload)):
            logger.info(f"uploading file {index+1:>{len(str(number_of_files))}}/{number_of_files}: '{file}'")
            mimetype, _ = mimetypes.guess_type(file) # required by bunkr to generate preview of images
            logger.debug(f"MIME type for {file} is: {mimetype}")
            files = {'files[]': (file, open(file, 'rb'), mimetype)}

            try:
                response = self.session.post(
                    server,
                    files=files,
                    params = {'createImageThumbnails': 1},
                    headers={
                        'albumid': str(album_id),
                        'token': self.token
                    }
                )
                if  response.status_code == 200:
                    logger.info({'success': True,'name': response.json()['files'][0]['name'],'url':response.json()['files'][0]['url']})
                    logger.debug(response.text)

                else:
                    logger.error({'status': 'False', 'response': response.text})
                    continue

            except Exception as e:
                logger.error(f'upload of {file} failed - HTTP_error_code: {e}')
                continue

        return album_url
    
    def read_cookies_from_file(self,json_cookies_file):
        cookies={}
        with open( json_cookies_file, 'r', encoding ='utf-8') as f:
            cookies_dump=json.load(f)
        for item in cookies_dump:
            cookies[item["name"]] = item["value"]
        self.session.cookies.update(cookies)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
    description='Example: bunkr <file/folder_path>')
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
        '-C',
        '--cookies_file', dest='cookies_file',
        help=
        'Path to you cookies file (json format)')
    parser.add_argument(
        '-c',
        '--config_file', dest='config_file',
        help=
        'Path to your confie file (json format). Overrodes -t, -T  and -C ')
    parser.add_argument(
        '-n',
        '--album_name', dest='album_name',
        help=
        'album to use')
    parser.add_argument(
        '-T',
        '--api_token', dest='token_file', default=None,
        help=
        'Path to file containing your TOKEN (plain text)')
    parser.add_argument(
        '-t',
        '--token', dest='token', default=None,
        help=
        'Your bunkr TOKEN')
    
    return parser.parse_args()

if __name__ == "__main__":
    
    args = parse_arguments()
    if not args.config_file:
        logger.debug('did not provide config file')
        if not (args.token and args.cookies_file):
            logger.error('did not provide cookies and/or token, exiting...')
            exit(1)
        else:
            bunkr_conn=bunkr(args.token,cookies_file=args.cookies_file)

    else:
        with open(args.config_file, 'r', encoding = 'utf8') as f:
            _=json.load(f)
        bunkr_conn=bunkr(_['token'], _['cookies'])

    logger.error('stand along use not implemented yet')