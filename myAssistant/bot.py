# bot.py

# speechrecognition, pyaudio, brew install portaudio
import os
import sys
sys.path.append("./")
from subprocess import call

call(["source", "env.sh"])

import requests
import datetime
import dateutil.parser
import json
import traceback
import gevent
import multiprocessing
from nlg import NLG
from speech import Speech
from knowledge import Knowledge
from vision import Vision
from local_bot import get_response

MY_NAME = "Happiest Mind"
LAUNCH_PHRASE = "ok smart"
USE_LAUNCH_PHRASE = True
WEATHER_API_TOKEN = os.environ.get("weather_api_token", "")
WEATHER_AI_TOKEN = os.environ.get("wit_ai_token", "")
DEBUGGER_ENABLED = True
CAMERA = 0
SEARCH_IN_LOCAL_BOT = True


class Bot(object):
    def __init__(self):
        self.nlg = NLG(user_name=MY_NAME)
        self.speech = Speech(launch_phrase=LAUNCH_PHRASE, debugger_enabled=DEBUGGER_ENABLED)
        self.knowledge = Knowledge(WEATHER_API_TOKEN)
        self.vision = Vision(camera=CAMERA)

    def start(self):
        """
        Main loop. Waits for the launch phrase, then decides an action.
        :return:
        """
        self.__appearance_action()
        requests.get("http://localhost:8080/clear")
        while True:
            if self.vision.recognize_face():
                if USE_LAUNCH_PHRASE:
                    recognizer, audio = self.speech.listen_for_audio()
                    if self.speech.is_call_to_action(recognizer, audio):
                        self.__acknowledge_action()
                        self.decide_action()
                else:
                    self.decide_action()

    def decide_action(self):
        """
        Recursively decides an action based on the intent.
        :return:
        """
        self.__appearance_action()
        recognizer, audio = self.speech.listen_for_audio()

        # received audio data, now we'll recognize it using Google Speech Recognition
        speech = self.speech.google_speech_recognition(recognizer, audio)
        #import ipdb;ipdb.set_trace()

        if speech is not None:
            try:
                res_spawn = gevent.spawn(get_response, speech)
                res_spawn.start()
                r = requests.get('https://api.wit.ai/message?v=26/04/2017&q=%s' % speech,
                                 headers={"Authorization": WEATHER_AI_TOKEN})
                print "Response from wit.ai", r.text
                json_resp = json.loads(r.text)
                entities = None
                intent = None
                if 'entities' in json_resp and 'intent' in json_resp['entities']:
                    entities = json_resp['entities']
                    intent = json_resp['entities']['intent'][0]["value"]

                print intent
                if intent == 'greeting':
                    self.__text_action(self.nlg.greet())
                elif intent == 'snow white':
                    self.__text_action(self.nlg.snow_white())
                elif intent == 'weather':
                    self.__weather_action(entities)
                elif intent == 'news':
                    self.__news_action()
                elif intent == 'maps':
                    print entities
                    self.__maps_action(entities)
                elif intent == 'holidays':
                    self.__holidays_action()
                elif intent == 'appearance':
                    self.__appearance_action()
                elif intent == 'user status':
                    self.__user_status_action(entities)
                elif intent == 'user name':
                    self.__user_name_action()
                elif intent == 'personal status':
                    self.__personal_status_action()
                elif intent == 'joke':
                    self.__joke_action()
                elif intent == 'insult':
                    self.__insult_action()
                    return
                elif intent == 'appreciation':
                    self.__appreciation_action()
                    return
                elif intent == 'general':
                    self.__text_action("I am building myself, will take time to respond it")
                else: # No recognized intent
                    #import ipdb;ipdb.set_trace()
                    if SEARCH_IN_LOCAL_BOT:
                        self.__text_action("My AI can't find any action for this. Let me check, if locale bot can help something")
                        self.__appearance_action()
                        gevent.joinall([res_spawn])
                        print "Response from bot: ",  res_spawn.value
                        self.__text_action(res_spawn.value)
                        #import ipdb;ipdb.set_trace()
                    else:
                        self.__text_action("I'm sorry, I don't know about that yet.")
                        return

            except Exception as e:
                print "Failed wit!"
                print(e)
                traceback.print_exc()
                self.__text_action("I'm sorry, I couldn't understand what you meant by that")
                return

            self.decide_action()
    
    def __general_action(self, nlu_entities=None):
        res_text = ""
        if nlu_entities is not None:
            if 'general' in nlu_entities:
                res_text = nlu_entities['general'][0]["value"]
        if res_text:
            self.__text_action(res_text)
        else:
            self.__text_action("I should not say something, which I don't know.")

    def __joke_action(self):
        joke = self.nlg.joke()

        if joke is not None:
            self.__text_action(joke)
        else:
            self.__text_action("I couldn't find any jokes")

    def __user_status_action(self, nlu_entities=None):
        attribute = None

        if (nlu_entities is not None) and ("Status_Type" in nlu_entities):
            attribute = nlu_entities['Status_Type'][0]['value']

        self.__text_action(self.nlg.user_status(attribute=attribute))

    def __user_name_action(self):
        if self.nlg.user_name is None:
            self.__text_action("I don't know your name. You can configure it in bot.py")

        self.__text_action(self.nlg.user_name)

    def __appearance_action(self):
        requests.get("http://localhost:8080/face")

    def __appreciation_action(self):
        self.__text_action(self.nlg.appreciation())

    def __acknowledge_action(self):
        self.__text_action(self.nlg.acknowledge())

    def __insult_action(self):
        self.__text_action(self.nlg.insult())

    def __personal_status_action(self):
        self.__text_action(self.nlg.personal_status())

    def __text_action(self, text=None):
        if text is not None:
            requests.get("http://localhost:8080/statement?text=%s" % text)
            self.speech.synthesize_text(text)

    def __news_action(self):
        headlines = self.knowledge.get_news()

        if headlines:
            requests.post("http://localhost:8080/news", data=json.dumps({"articles":headlines}))
            self.speech.synthesize_text(self.nlg.news("past"))
            interest = self.nlg.article_interest(headlines)
            if interest is not None:
                self.speech.synthesize_text(interest)
        else:
            self.__text_action("I had some trouble finding news for you")

    def __weather_action(self, nlu_entities=None):

        current_dtime = datetime.datetime.now()
        skip_weather = False # used if we decide that current weather is not important

        weather_obj = self.knowledge.find_weather()
        temperature = weather_obj['temperature']
        icon = weather_obj['icon']
        wind_speed = weather_obj['windSpeed']

        weather_speech = self.nlg.weather(temperature, current_dtime, "present")
        forecast_speech = None

        if nlu_entities is not None:
            #import ipdb;ipdb.set_trace()
            self.nlg.acknowledge = nlu_entities["datatime"][0]
            if 'datetime' in nlu_entities:
                if 'grain' in nlu_entities['datetime'][0] and nlu_entities['datetime'][0]['grain'] == 'day':
                    dtime_str = nlu_entities['datetime'][0]['value'] # 2016-09-26T00:00:00.000-07:00
                    dtime = dateutil.parser.parse(dtime_str)
                    if current_dtime.date() == dtime.date(): # hourly weather
                        forecast_obj = {'forecast_type': 'hourly', 'forecast': weather_obj['daily_forecast']}
                        forecast_speech = self.nlg.forecast(forecast_obj)
                    elif current_dtime.date() < dtime.date(): # sometime in the future ... get the weekly forecast/ handle specific days
                        forecast_obj = {'forecast_type': 'daily', 'forecast': weather_obj['weekly_forecast']}
                        forecast_speech = self.nlg.forecast(forecast_obj)
                        skip_weather = True
            if 'Weather_Type' in nlu_entities:
                weather_type = nlu_entities['Weather_Type'][0]['value']
                print weather_type
                if weather_type == "current":
                    forecast_obj = {'forecast_type': 'current', 'forecast': weather_obj['current_forecast']}
                    forecast_speech = self.nlg.forecast(forecast_obj)
                elif weather_type == 'today':
                    forecast_obj = {'forecast_type': 'hourly', 'forecast': weather_obj['daily_forecast']}
                    forecast_speech = self.nlg.forecast(forecast_obj)
                elif weather_type == 'tomorrow' or weather_type == '3 day' or weather_type == '7 day':
                    forecast_obj = {'forecast_type': 'daily', 'forecast': weather_obj['weekly_forecast']}
                    forecast_speech = self.nlg.forecast(forecast_obj)
                    skip_weather = True


        weather_data = {"temperature": temperature, "icon": icon, 'windSpeed': wind_speed, "hour": datetime.datetime.now().hour}
        requests.post("http://localhost:8080/weather", data=json.dumps(weather_data))

        if not skip_weather:
            self.speech.synthesize_text(weather_speech)

        if forecast_speech is not None:
            self.speech.synthesize_text(forecast_speech)

    def __maps_action(self, nlu_entities=None):

        location = None
        map_type = None
        if nlu_entities is not None:
            if 'location_name' in nlu_entities:
                location = nlu_entities['location_name'][0]["value"]
            if "Map_Type" in nlu_entities:
                map_type = nlu_entities['Map_Type'][0]["value"]

        #import ipdb;ipdb.set_trace()
        if location is not None:
            maps_url = self.knowledge.get_map_url(location, map_type)
            maps_action = "Sure. Here's a map of %s." % location
            body = {'url': maps_url}
            requests.post("http://localhost:8080/image", data=json.dumps(body))
            self.speech.synthesize_text(maps_action)
        else:
            self.__text_action("I'm sorry, I couldn't understand what location you want.")

    def __holidays_action(self):
        holidays = self.knowledge.get_holidays()
        next_holiday = self.__find_next_holiday(holidays)
        requests.post("http://localhost:8080/holidays", json.dumps({"holiday": next_holiday}))
        self.speech.synthesize_text(self.nlg.holiday(next_holiday['localName']))

    def __find_next_holiday(self, holidays):
        today = datetime.datetime.now()
        for holiday in holidays:
            date = holiday['date']
            if (date['day'] > today.day) and (date['month'] > today.month):
                return holiday

        # next year
        return holidays[0]

if __name__ == "__main__":
    bot = Bot()
    bot.start()
