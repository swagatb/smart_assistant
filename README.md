# Build an Assistant, combining 
## - SmartMirror(https://github.com/MichMich/MagicMirror), 
## - A Localchatbot
## - Google Assistant

# Setup Guide

Download the stable version of Node.js: 
`https://nodejs.org/en/`

Clone the latest code from gitlab:

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
 
Navigate to `myAssistant` folder

Install ffmpeg
```
apt-get install ffmpeg
```

Use `setup.sh` to install dependencies
```shell
sudo ./setup.sh
```

Create `env.sh` file in `myAssistant` directory and add below credential to it
```
#! /bin/bash
export weather_api_token="<key>" # weather.com api key
export wit_ai_token="Bearer <key>" # wit.ai token
export SPEECH_KEY="<key>" # google speach API
```

Make sure GUI is running, then start the AI
```shell
python bot.py
```


