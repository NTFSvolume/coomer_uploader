## coomer_uploader

![Preview](https://images2.imgbox.com/d0/79/M9BZEq4D_o.png)

## Features

 - Album/folder uploading instead of individually.

## Requirements

[Python 3.9+](https://www.python.org/) 

`python3 -m pip install -r requirements.txt`

## Running

run the main script:

`python3 main.py`

## Authentication

Uploading to Bunkr requires an account. You will need to get the account's token from your dashboard section. 

You also need to provide your account cookies (as json) cause Bunkr disabled file upload without login in.
You can get then using [Cookie-Editor](https://github.com/moustachauve/cookie-editor) on your browser

You also need to provide an album name that doesn't already exist in your account.

## Supported Hosts

- [Gofile](https://gofile.io/)
- [Pixeldrain](https://pixeldrain.com/)
- [Bunkr](https://bunkr.si/)

## Known bugs
- Photos uploaded to pixeldrain do not get a thumbnail autogenerated

## Todo

- [ ] enable upload by chunks
- [ ] upload progress report (x out of y files uploaded, z errors)
- [ ] upload to pixeldrain with account (auth via API-Key)
- [ ] upload to gofile with account (auth via API-Key)
- [ ] auto retry errors
