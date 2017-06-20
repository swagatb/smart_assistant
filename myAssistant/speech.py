# speech.py
# speechrecognition, pyaudio, brew install portaudio
import speech_recognition as sr
import os
import requests
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import pyaudio
import wave

SPEECH_KEY = os.environ.get("SPEECH_KEY")


class Speech(object):
    def __init__(self, launch_phrase="smart", debugger_enabled=False):
        self.launch_phrase = launch_phrase
        self.debugger_enabled = debugger_enabled
        self.__debugger_microphone(enable=False)

    def google_speech_recognition(self, recognizer, audio):
        speech = None
        try:
            speech = recognizer.recognize_google(audio, key = SPEECH_KEY)
            print("Google Speech Recognition thinks you said " + speech)
        except sr.UnknownValueError:
            #import ipdb;ipdb.set_trace()
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

        return speech

    def listen_for_audio(self):
        # obtain audio from the microphone
        r = sr.Recognizer()
        m = sr.Microphone()
        with m as source:
            r.adjust_for_ambient_noise(source)
            self.__debugger_microphone(enable=True)
            print "I'm listening"
            audio = r.listen(source)

        self.__debugger_microphone(enable=False)
        print "Found audio"
        
        THRESHOLD = 500  # audio levels not normalised.
        CHUNK_SIZE = 1024
        SILENT_CHUNKS = 3 * 44100 / 1024  # about 3sec
        FORMAT = pyaudio.paInt16
        FRAME_MAX_VALUE = 2 ** 15 - 1
        NORMALIZE_MINUS_ONE_dB = 10 ** (-1.0 / 20)
        RATE = 44100
        CHANNELS = 1
        #import ipdb;ipdb.set_trace()
        TRIM_APPEND = RATE / 4
        """
        wave_file = wave.open("/home/administrator/project/smart_mirror/myMirror/recieve", 'wb')
        wave_file.setnchannels(CHANNELS)
        wave_file.setsampwidth(audio.sample_width)
        wave_file.setframerate(RATE)
        wave_file.writeframes(audio.get_wav_data())
        wave_file.close()
        """
        return r, audio

    def is_call_to_action(self, recognizer, audio):
        speech = self.google_speech_recognition(recognizer, audio)

        #import ipdb;ipdb.set_trace()
        if speech is not None and self.launch_phrase in speech.lower():
            return True

        return False

    def synthesize_text(self, text):
        tts = gTTS(text=text, lang='en')
        tts.save("tmp.mp3")
        song = AudioSegment.from_mp3("tmp.mp3")
        play(song)
        os.remove("tmp.mp3")

    def __debugger_microphone(self, enable=True):
        if self.debugger_enabled:
            try:
                r = requests.get("http://localhost:8080/microphone?enabled=%s" % str(enable))
                if r.status_code != 200:
                    print("Used wrong endpoint for microphone debugging")
            except Exception as e:
                print(e)