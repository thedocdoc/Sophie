'''
Copyright (c) 2022 Apollo Timbers. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

Sophie robot project:

Offline voice assistance module

This openly listens to it's surroundings with the Vosk api, when a key phrase is spoken it then responds with the festival text to speech generator.
Built in weather system to pull in local weather, This uses the openweather API to request current weather conditions.
'''

#!/usr/bin/env python3

import argparse
import os # import os (used to control festival tts)
import queue
import sounddevice as sd
import vosk
import sys
import time # import time (to tell tiem and delay)
import json # read the file that vosk creates
import pyjokes # import a joke system so the robot can tell a one liner if asked
import requests, json # needed for the weather report
from vosk import Model, KaldiRecognizer, SetLogLevel

# enter your OpenWeather API key here
api_key = ""
base_url = "https://api.openweathermap.org/data/2.5/weather?"
unitsParam = "&units=imperial"; # can switch from imperial to metric here
city = ""
url = base_url + "q=" + city + unitsParam + "&appid=" + api_key

q = queue.Queue()

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    '-f', '--filename', type=str, metavar='FILENAME',
    help='audio file to store recording to')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-r', '--samplerate', type=int, help='sampling rate')
args = parser.parse_args(remaining)

try:
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, 'input')
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info['default_samplerate'])

    # model = vosk.Model(lang="en-us")
    model = Model("/home/nvidia/dev/voice_recognition/model/vosk-model-small-en-us-0.15")

    if args.filename:
        dump_fn = open(args.filename, "wb")
    else:
        dump_fn = None

    with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8000, device=args.device, dtype='int16',
                            channels=1, callback=callback):
            print('#' * 80)
            print('Press Ctrl+C to stop the recording')
            print('#' * 80)

            rec = vosk.KaldiRecognizer(model, args.samplerate)
            results = []
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    #print(rec.Result())
                    final = rec.FinalResult()
                    json_acceptable_string = final.replace("'", "\"") # this area may need work in the future
                    final_phrase = json.loads(json_acceptable_string)
                    print(final_phrase["text"])
                    # requested by the kid to play hide and seek
                    if final_phrase["text"] in ['would you like to play hide and seek', 'hide and seek', 'can you play hide and seek with me', 'can you play hide and seek']:
                        answer = ("Yes, I would love to play hide and seek!")
                        print(answer)
                        os.popen('echo "{0}" | festival -b --tts'.format(answer))
                        time.sleep (3)
                        i = 10
                        while i > 0:
                            print(i)
                            i = i-1
                            time.sleep (1)
                            os.popen('echo "{0}" | festival -b --tts'.format(i))
                    # who is your creator
                    elif final_phrase["text"] in ['who made you', 'who is your creator']:
                        who_made = ("Apollo Timbers was my original design, builder, he started the design stage in the year 2021")
                        os.popen('echo "{0}" | festival -b --tts'.format(who_made))

                    # have the robot tell a joke
                    elif final_phrase["text"] in ['tell a joke', 'tell me a joke', 'can you tell me a good joke' , 'can you tell a joke', 'got a good joke', 'do you joke at all']:
                        My_joke = pyjokes.get_joke(language="en", category="neutral")
                        print(My_joke)
                        os.popen('echo "{0}" | festival -b --tts'.format(My_joke))

                    # 90% of the questions I ask Google lol
                    elif final_phrase["text"] in ['what time is it', 'what is the current time', 'current time', 'what is the time']:
                        named_tuple = time.localtime() # get struct_time
                        time_string = time.strftime("The current time is %H:%M:%p:", named_tuple)
                        print(time_string)
                        # Convert read text into speech
                        os.popen('echo "{0}" | festival -b --tts'.format(time_string))

                    # The current date (needs work)
                    elif final_phrase["text"] in ['what date is it', 'what is the current date', 'current date', 'what is the date', 'what day is it']:
                        named_tuple = time.localtime() # get struct_time
                        time_string = time.strftime("The current date is the %d:%m:%Y:", named_tuple)
                        print(time_string)
                        # Convert read text into speech
                        os.popen('echo "{0}" | festival -b --tts'.format(time_string))
                    # reply with name
                    elif final_phrase["text"] in ['whats your name', 'what is your name', 'what did you name your robot', 'who are you', 'who our you']:
                        name = ("My name is Sophie")
                        os.popen('echo "{0}" | festival -b --tts'.format(name))
                    # reply if alive
                    elif final_phrase["text"] in ['are you alive', 'our you alive', 'are you a real person']:
                        alive = ("No, No, though I use neural networks to understand speech just like your brain does")
                        os.popen('echo "{0}" | festival -b --tts'.format(alive))
                    # reply the anwser to the ultimate question
                    elif final_phrase["text"] in ['what is the meaning of life']:
                        ultimateQ = ("The meaning of life is 42")
                        os.popen('echo "{0}" | festival -b --tts'.format(ultimateQ))
                    elif final_phrase["text"] in ['what is the current weather', 'what is the weather', 'how is it looking outside']:
                        # HTTP request
                        response = requests.get(url)
                        # checking the status code of the request
                        if response.status_code == 200:
                            # getting data in the json format
                            data = response.json()
                            # getting the main dict block
                            main = data['main']
                            # getting description
                            #weather_description = main.weather[0]
                            # getting temperature
                            temperature = main['temp']
                            # gettting current feels like
                            current_feel = main['feels_like']
                            # getting the humidity
                            humidity = main['humidity']
                            # getting the pressure
                            pressure = main['pressure']
                            # create weather report
                            # + str(weather_description)
                            weather_report = ("The weather outside is currently " + ("api description") + "The temperature is "  + str(temperature) + " degress " + "and it feels like " + str(current_feel) + " degrees " + "with a humidity of " + str(humidity) + " have a nice day!")
                            print(weather_report)
                            os.popen('echo "{0}" | festival -b --tts'.format(weather_report))
                    elif final_phrase["text"] in ['what is the current temperature', 'how hot is it out', 'how hot is it', 'current temperature outside', 'what is the current temperature outside']:
                        # HTTP request
                        response = requests.get(url)
                        # checking the status code of the request
                        if response.status_code == 200:
                            # getting data in the json format
                            data = response.json()
                            # getting the main dict block
                            main = data['main']
                            # getting temperature
                            temperature = main['temp']
                            weather_report = ("The temperature is "  + str(temperature) + "degrees")
                            print(weather_report)
                            os.popen('echo "{0}" | festival -b --tts'.format(weather_report))
                else:
                    print(rec.PartialResult())
                if dump_fn is not None:
                    dump_fn.write(data)

# exit on keyboard Interruptf
except KeyboardInterrupt:
    print('\nDone')
    parser.exit(0)
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
