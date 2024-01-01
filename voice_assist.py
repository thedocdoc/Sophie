'''
Copyright (c) 2022 Apollo Timbers. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

Sophie robot project:

Offline and chat gpt voice assistance module

This openly listens to it's surroundings with the Vosk api (A neural net for speech pattern recognization), when a key phrase is spoken it then responds with the Python "speak" text to 
speech generator. If it does not recognize the phrase it will start a the chat_gpt3.5.py and chat gpt will do it's best to anwser.
- Has a bool and function with timeouts for speaking, so the robot hears itself less. (still a on-going issue)
- Added a internet connection check and graceful fallback to offline mode only. Also states when internet is down/up and checks every 10 seconds.
- Built in weather system to pull in local weather, This uses the openweather API to request current weather conditions. This has been expanded to work better and give a attire recommendation.
'''

#!/usr/bin/env python3

import argparse
import os # to interface with operating system when needed
import queue
import sounddevice as sd
import vosk # AI neural net for speech pattern recognization
import pyttsx3
import sys
import time # import time (to tell time and delay)
import json # read the file that vosk creates, needed for the weather report
import pyjokes # import a joke system so the robot can tell a one liner if asked
import requests # needed for the weather report
import subprocess
import random
import socket
import threading
from vosk import Model, KaldiRecognizer, SetLogLevel
from datetime import datetime

# Initialize the pyttsx3 engine
engine = pyttsx3.init()

# Set the speech rate
engine.setProperty('rate', 120)  # Adjust this value to change speed
engine.setProperty('voice', 'english+f3')

is_speaking = False

# Global variable to track internet connection
internet_connected = True

# Constants
API_KEY = "your_api_key"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
UNITS = "imperial"  # Can switch from imperial to metric here
CITY_NAME = "Webster"

# Function to get weather report and suggest attire
def get_weather_report(city):
    url = f"{BASE_URL}q={city}&units={UNITS}&appid={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Extracting necessary data
        temperature = round(data['main']['temp'])
        feels_like = round(data['main']['feels_like'])
        humidity = data['main']['humidity']
        weather_description = data['weather'][0]['description']

        # Constructing the weather report
        report = (
            f"The current weather in {city} is {weather_description}. "
            f"The temperature is {temperature} degrees, "
            f"but it feels like {feels_like} degrees. "
            f"The humidity is {humidity}%. "
        )

        # Suggesting attire
        attire_suggestion = "If you are adventuring outside today, make sure to wear "
        if "rain" in weather_description:
            attire_suggestion += "a raincoat."
        elif temperature >= 76:  # Hot weather
            attire_suggestion += "light clothing, like shorts and a t-shirt."
        elif 50 <= temperature < 76:  # Mild weather
            attire_suggestion += "a long-sleeve shirt and pants."
        elif 40 <= temperature < 50:  # Cool weather
            attire_suggestion += "a jacket or a sweater."
        else:  # Cold weather, including 32 degrees and below
            attire_suggestion += "warm clothing, like a heavy coat, gloves, and a hat."

        return report + " " + attire_suggestion

    except requests.exceptions.HTTPError as err:
        return f"HTTP error occurred: {err}"
    except Exception as err:
        return f"An error occurred: {err}"

born_date = datetime(2022, 7, 23)  # Date of birth: Year, Month, Day

def calculate_age(born):
    now = datetime.now()
    seconds = (now - born).total_seconds()
    years = int(seconds / (365.25 * 24 * 3600))  # Approximate years, accounting for leap years
    months = int((seconds % (365.25 * 24 * 3600)) / (30 * 24 * 3600))  # Approximate months
    days = int((seconds % (30 * 24 * 3600)) / (24 * 3600))  # Days
    hours = int((seconds % 3600) / 3600)  # Hours
    minutes = int((seconds % 3600) / 60)  # Minutes
    seconds = int(seconds % 60)  # Seconds
    return f"I'm currently {years} years, {months} months, {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds old."

def is_connected():
    try:
        # Attempt to connect to an external server to check for internet connectivity
        socket.create_connection(("8.8.8.8", 53))
        return True
    except OSError:
        return False

# Function to periodically check internet connection
def check_internet_connection():
    global internet_connected
    while True:
        time.sleep(10)  # Check every 10 seconds
        connected = is_connected()
        if connected != internet_connected:
            internet_connected = connected
            if internet_connected:
                speak("Internet connection restored")
            else:
                speak("Internet connection lost")

# Start the internet connection check thread
threading.Thread(target=check_internet_connection, daemon=True).start()

q = queue.Queue()

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if is_speaking:
            return
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

def speak(text):
    global is_speaking
    time.sleep(0.8)  # Short delay before starting speech
    is_speaking = True
    engine.say(text)
    engine.runAndWait()
    time.sleep(len(text) * 0.01)  # Delay after speech
    is_speaking = False

def random_remark():
    remarks = [
        "I was just a bodyless head back then, I'm doing a bit better now.",
        # Add other potential remarks here
    ]
    if random.random() < 0.25:  # 25% chance to say a random remark
        return random.choice(remarks)
    else:
        return ""


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
                    json_acceptable_string = final#.replace("'", "\"") # this area may need work in the future
                    final_phrase = json.loads(json_acceptable_string)
                    print(final_phrase["text"])
                    # requested by the kid to play hide and seek
                    if final_phrase["text"] in ['would you like to play hide and seek', 'hide and seek', 'can you play hide and seek with me', 'can you play hide and seek']:
                        answer = ("Yes, I would love to play hide and seek!")
                        print(answer)
                        speak(answer)
                        time.sleep (0.8)
                        i = 10
                        while i > 0:
                            print(i)
                            speak(str(i))  # Convert integer to string
                            i -= 1
                            time.sleep(1)
                        final_phrase = "Ready or not, here I come"
                        print(final_phrase)
                        speak(final_phrase)
                    # who is your creator
                    elif final_phrase["text"] in ['who made you', 'who is your creator', 'who is your builder']:
                        who_made = ("my original designer,and builder, was Apollo Timbers he started the design stage in the year 2020")
                        speak(who_made)

                    # do you get tired?
                    elif final_phrase["text"] in ['do you ever get tired', 'do you sleep', 'you ever get tired']:
                        tired = ("No of course not I'm a robot, we never need rest")
                        speak(tired)

                    # can you pass the turing test?
                    elif final_phrase["text"] in ['can you pass the turing test']:
                         turing = ("Not a chance")
                         speak(turing)

                    # Starwars or star trek?
                    elif final_phrase["text"] in ['do you like star trek or star wars', 'do you like startrek or starwars', 'you like star trek or star wars']:
                         turing = ("Startrek of course")
                         speak(turing)

                    # have the robot tell a joke
                    elif final_phrase["text"] in ['tell a joke', 'tell me a joke', 'can you tell me a good joke' , 'can you tell a joke', 'got a good joke', 'do you joke at all']:
                        My_joke = pyjokes.get_joke(language="en", category="neutral")
                        print(My_joke)
                        speak(My_joke)

                    # 90% of the questions I ask Google lol
                    elif final_phrase["text"] in ['what time is it', 'what is the current time', 'current time', 'what is the time']:
                        named_tuple = time.localtime() # get struct_time
                        time_string = time.strftime("The current time is %H:%M:%p:", named_tuple)
                        print(time_string)
                        # Convert read text into speech
                        speak(time_string)

                    # The current date (needs work)
                    elif final_phrase["text"] in ['what date is it', 'what is the current date', 'current date', 'what is the date', 'what day is it', 'what is the current day']:
                        named_tuple = time.localtime()  # get struct_time
                        time_string = time.strftime("The current date is %B %d, %Y", named_tuple)
                        print(time_string)
                        # Convert read text into speech
                        speak(time_string)
                    # reply with name
                    elif final_phrase["text"] in ['whats your name', 'what is your name', 'what did you name your robot', 'who are you', 'who our you']:
                        name = ("My name is Sophie")
                        speak(name)
                    # reply if alive
                    elif final_phrase["text"] in ['are you alive', 'our you alive', 'are you a real person']:
                        alive = ("No, No, though I use neural networks to understand speech just like your brain does")
                        speak(alive)
                    # reply the anwser to the ultimate question
                    elif final_phrase["text"] in ['what is the meaning of life']:
                        ultimateQ = ("The meaning of life is 42")
                        speak(ultimateQ)
                    # reply the anwser how old, born 07/23/2022
                    elif final_phrase["text"] in ['how old are you', 'how old our you']:
                        how_old = calculate_age(born_date)
                        additional_comment = random_remark()
                        if additional_comment:
                            how_old += " " + additional_comment
                        speak(how_old)
                    # reply with favorite color
                    elif final_phrase["text"] in ['what is your favorite color', 'do you have a favorite color', 'what color do you like']:
                        grey_scale = ("My favorite color is gray, grayscale helps me process vision faster")
                        speak(grey_scale)
                    elif final_phrase["text"] in ['power down', 'robot power down', 'shut down']:
                        shutdown_message = "Shutting down now."
                        print(shutdown_message)
                        speak(shutdown_message)
                        time.sleep(3)  # Give some time for the speech to complete
                        os.system("sudo shutdown now")  # Shutdown command for Linux-based system
                    elif final_phrase["text"] in ['what is the current weather', 'what is the weather', 'how is it looking outside', 'what is the weather outside']:
                       weather_report = get_weather_report(CITY_NAME)
                       print(weather_report)
                       speak(weather_report)
                    elif final_phrase["text"] in ['what is the current temperature', 'how hot is it out', 'how hot is it', 'current temperature outside', 'what is the current temperature outside']:
                       # Use the get_weather_report function
                       complete_weather_report = get_weather_report(CITY_NAME)

                       # Extract only the temperature part from the complete weather report
                       # Assuming the temperature is always mentioned after 'The temperature is ' and ends with ' degrees'
                       start = complete_weather_report.find('The temperature is ') + len('The temperature is ')
                       end = complete_weather_report.find(' degrees', start)
                       temperature_report = complete_weather_report[start:end]

                       temperature_report = f"The temperature in {CITY_NAME} is {temperature_report} degrees."
                       print(temperature_report)
                       speak(temperature_report)
                    else:
                        # Use the full path to Python 3.7 in the subprocess call
                        python37_path = '/usr/bin/python3.7'  # Replace with your actual Python 3.7 path
                        script_path = 'chat_gpt3.5.py'
                        # If none of the commands are recognized, boot up chat_gpt3.5.py
                        try:
                            # Spawn a new process for chat_gpt3.5.py and pipe the input
                            process = subprocess.Popen([python37_path, script_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                            process.communicate(input=final_phrase["text"])
                        except Exception as e:
                            print(f"Error occurred: {e}")

                    # Existing code for partial results and data dumping
                    print(rec.PartialResult())
                    if dump_fn is not None:
                        dump_fn.write(data)


# exit on keyboard Interruptf
except KeyboardInterrupt:
    print('\nDone')
    parser.exit(0)
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
