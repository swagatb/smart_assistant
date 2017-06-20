# Build an Assistant, combining 
# - SmartMirror(https://github.com/MichMich/MagicMirror), 
# - A Localchatbot
# - Google Assistant

## Setup Guide

## Magic Mirror
Download the stable version of Node.js: 
https://nodejs.org/en/

Clone the latest code from:

Navigate inside the GUI folder

Install dependencies
```shell
sudo npm install
```
 
Verify it starts
```shell
npm start
```
 
## AI
 
Make sure Ruby is installed: https://www.ruby-lang.org/en/documentation/installation/
 
Install Homebrew: http://brew.sh/
 
Navigate to the myAssistant folder

Install ffmpeg
```
apt-get install ffmpeg
```

Use `setup.sh` to create a virtual environment and install dependencies
```shell
sudo ./setup.sh
```

Replace wit.ai and darksky.net tokens in the `bot.py` file

Make sure GUI is running, then start the AI
```shell
python bot.py
```


