'''
Copyright (c) 2022 Apollo Timbers. All rights reserved.

This work is licensed under the terms of the Apache License 2.0.
For a copy, see https://github.com/apache/.github/blob/main/LICENSE.

Sophie robot project:

Offline and chat gpt voice assistance module

This openly listens to it's surroundings with the Vosk api (A neural net for speech pattern recognization), when a key phrase is spoken it then responds with the Python "speak" text to
speech generator. If it does not recognize the phrase it will start up the chat_gpt4.py and chat gpt will do it's best to anwser.

Change log:
- Added a internet connection check and graceful fallback to offline mode only. Also states when internet is down/up and checks every 15 seconds.
- Built in weather system to pull in local weather, This uses the openweather API to request current weather conditions. This has been expanded to work better and give attire recommendations.
- Added logging and removed the print statements, this sped up the program quite a bit.
- Restructured code for speed and also now it only loads the vosk model at the start only once
- Enhanced date born function, it is also now more accurate actual lengths of months and accounting for leap years
- Connected to the pyttsx3 engine, now the program knows when it is speaking and does not talk to itself. This is a huge milestone.
- Added a semaphore file creation/deletion process to help debug the robot hearing itself and sync with chat_gpt4.py, so far no dice
- Made the time function more natural sounding and state am/pm
- Refactored code, reduce main down and add dictionary for the offline phrases
- Turned weather function into a class, it was getting quite large

Future work
- The chat_gpt4 module is still needing work in this area, that I may end up removing. Still attemptting to find a resolve
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
import logging
from vosk import Model, KaldiRecognizer, SetLogLevel
from datetime import datetime
from dateutil.relativedelta import relativedelta
from weather_service import WeatherService  # Import the class from weather_service.py


semaphore_path = "speaking_semaphore.txt"

#weather_service api
api_key = "your_api_key"
weather_service = WeatherService(api_key)  # Instantiate the service
CITY_NAME = "webster"

# Delete semaphore file at the start if it exists
if os.path.exists(semaphore_path):
    try:
        os.remove(semaphore_path)
    except OSError as e:
        logging.error(f"Error deleting semaphore file: {e}")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# To also log to a file, add filename='myapp.log' in basicConfig

# Initialize the Vosk model at the start
model_path = "/home/nvidia/dev/voice_recognition/model/vosk-model-small-en-us-0.15"
model = vosk.Model(model_path)

# Global variable to track internet connection
internet_connected = True
is_speaking = False

# Initialize the pyttsx3 engine
engine = pyttsx3.init()

# Set the speech rate
engine.setProperty('rate', 120)  # Adjust this value to change speed
engine.setProperty('voice', 'english+f3')

def unmute_microphone():
    time.sleep(2.5)  # Delay before unmuting
    os.system("pactl set-source-mute alsa_input.usb-SEEED_ReSpeaker_4_Mic_Array__UAC1.0_-00.analog-mono 0")

# Callback functions for speech
def on_speak_start(name, location, length):
    global is_speaking
    is_speaking = True
    logging.info("Started speaking")

def on_speak_end(name, completed):
    global is_speaking
    is_speaking = False
    logging.info("Speaking completed")

# Connect the callbacks to the pyttsx3 engine
engine.connect('started-Word', on_speak_start)
engine.connect('finished-Word', on_speak_end)

def speak(text):
    """
        This function handles the text-to-speech (TTS) process. It ensures that the robot does not overlap its speech
        or respond to its voice. It uses a semaphore file mechanism to synchronize speaking activities. The function
        waits if it detects an ongoing speech or the semaphore file's presence, indicating another speech process is active.
        Once it's clear, the function initiates speech, creates a semaphore file to indicate it's speaking, and then
        proceeds to vocalize the text using the pyttsx3 engine. After speaking, it cleans up by deleting the semaphore file
        and resetting the speech flag.
    """
    global is_speaking
    semaphore_path = "speaking_semaphore.txt"

    # Wait if already speaking or semaphore exists
    while os.path.exists(semaphore_path) or is_speaking:
        time.sleep(0.1)

    is_speaking = True
    try:
        # Create the semaphore file
        with open(semaphore_path, "w") as f:
            pass

        engine.say(text)
        engine.runAndWait()

    finally:
        is_speaking = False
        # Safely delete the semaphore file
        try:
            os.remove(semaphore_path)
        except OSError:
            pass  # Handle the error if needed



born_date = datetime(2022, 7, 23)  # Date of birth: Year, Month, Day

def calculate_age(born):
    now = datetime.now()
    delta = relativedelta(now, born)
    return f"I'm currently {delta.years} years, {delta.months} months, {delta.days} days, {delta.hours} hours, {delta.minutes} minutes, and {delta.seconds} seconds old."

def is_connected():
    try:
        # Attempt to connect to an external server to check for internet connectivity
        socket.create_connection(("8.8.8.8", 53))
        return True
    except OSError:
        return False

# Function to periodically check internet connection
def check_internet_connection():
    """
        Periodically checks for internet connectivity by attempting to create a socket connection to an external server
        (Google's DNS in this case). This function runs in a separate thread and checks for connectivity every 15 seconds.
        The global variable 'internet_connected' is updated based on the connection status. If a change in the status is
        detected (i.e., from connected to disconnected or vice versa), the robot vocalizes the change in connectivity status.
        This function is crucial for determining the robot's ability to access online features and services, like the
        Chat GPT module or the weather API, and switch to offline functionalities when the internet is unavailable.
    """
    global internet_connected
    while True:
        time.sleep(15)  # Check every 15 seconds
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
    """
        This function is a callback for the SoundDevice library, called for each block of audio data (frame) captured by
        the microphone. It checks if the robot is currently speaking to avoid processing its voice. If a status error occurs,
        it is logged for debugging. The function places the captured audio data into a queue ('q'), which will be processed
        by the speech recognition system. This setup allows for continuous and asynchronous audio data handling, crucial for
        real-time voice recognition and responsiveness of the robot.
    """
    if is_speaking:
            return
    if status:
        logging.debug(status, file=sys.stderr)
    q.put(bytes(indata))

def random_remark():
    remarks = [
        "I was just a bodyless head back then, I'm doing a bit better now.",
        # Add other potential remarks here
    ]
    if random.random() < 0.25:  # 25% chance to say a random remark
        return random.choice(remarks)
    else:
        return ""

# Command function definitions
"""
    This section forms the core of the voice command interface, where functions corresponding to specific voice commands are defined.
    Each function is designed to execute a unique set of actions when the robot identifies a matching phrase via the Vosk API.
    The actions range from engaging the robot in interactive games, like hide and seek, to informative responses about the robot's
    origins or functionality.

    The modular architecture of this section is pivotal. It allows for the clean separation of command logic,
    making the code easier to understand and maintain. This structure is particularly beneficial when the voice command system
    needs to be expanded or modified, as it can be done without major overhauls to the existing codebase.
    Additionally, this setup contributes to the scalability of the project. As new features or requirements emerge, new command
    functions can be seamlessly added. Each new function simply needs to be defined here and then linked to an appropriate
    trigger phrase.

    This approach enhances the interactive capabilities of the robot, ensuring a more robust and reliable voice interaction experience.
"""

# report the current time voice command
def current_time(final_phrase):
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    am_pm = "am" if hour < 12 else "pm"

    # Convert to 12-hour format
    hour = hour % 12 or 12  # Converts '0' to '12'

    # Format the time string
    time_string = f"It is {hour}:{minute:02d} {am_pm}."
    logging.debug(time_string)
    # Convert read text into speech
    speak(time_string)

# report the weather voice command
def report_weather(final_phrase):
    weather_report = weather_service.get_weather_report(CITY_NAME)
    logging.info(weather_report)
    speak(weather_report)

def outside_temp(final_phrase):
    temperature = weather_service.get_temperature(CITY_NAME)
    if isinstance(temperature, str):  # Error message returned
        logging.error(temperature)
        speak("I'm sorry, I couldn't fetch the temperature.")
    else:
        temperature_report = f"The temperature in {CITY_NAME} is {temperature} degrees."
        logging.info(temperature_report)
        speak(temperature_report)

# play hide and seek voice command
def play_hide_and_seek(final_phrase):
    answer = ("Yes, I would love to play hide and seek!")
    logging.info(answer)
    speak(answer)
    time.sleep (0.8)
    i = 10
    while i > 0:
        logging.debug(i)
        speak(str(i))  # Convert integer to string
        i -= 1
        time.sleep(0.5)
    final_phrase = "Ready or not, here I come"
    logging.info(final_phrase)
    speak(final_phrase)

# take a picture on voice command
def take_picture_command(final_phrase):
    photo = ("Taking a picture now")
    # Command to take a picture is recognized
    speak(photo)
    try:
        # Replace '/path/to/zed_snap.py' with the actual path to the script
        subprocess.run(['python', '/home/nvidia/dev/Sophie/zed_snap.py'], check=True)
        logging.info("Picture taken successfully.")
    except subprocess.CalledProcessError as e:
        logging.info("Failed to take picture:", e)

# tell a joke offline version
def tell_joke(final_phrase):
    My_joke = pyjokes.get_joke(language="en", category="neutral")
    logging.debug(My_joke)
    speak(My_joke)


# respond to creator voice command
def respond_to_creator_inquiry(final_phase):
    who_made = ("my original designer,and builder, was Apollo Timbers, he started the design stage in the year 2020. The final build was at the end of 2023/beginning of 2024")
    speak(who_made)

# respond to user question of tiredness voice command
def do_you_get_tired(final_phrase):
    tired = ("No of course not I'm a robot, we never need rest")
    speak(tired)

# robots favorite color
def favorite_color(final_phrase):
    grey_scale = ("My favorite color is gray, grayscale helps me process vision faster")
    speak(grey_scale)


# Setup and Model Loading
"""
This section is responsible for setting up the audio input system and loading the Vosk model for speech recognition. Initially,
it defines essential parameters like the sampling rate, block size, and the audio input device. These parameters are crucial for
ensuring that the audio input is correctly captured and processed by the system.

- The 'model_path' specifies the location of the Vosk model. This model is a pre-trained neural network that the Vosk API utilizes
for recognizing and interpreting spoken words. Loading this model is a critical step, as it equips the robot with the ability to
understand human speech.

- After defining these parameters, the script creates an instance of the SoundDevice's RawInputStream. This input stream is configured
with the defined audio parameters and is responsible for continuously capturing audio data from the specified input device.

- Simultaneously, a KaldiRecognizer object from the Vosk API is instantiated. This recognizer works in tandem with the audio input stream.
It processes the audio data, applying the speech recognition model to convert spoken words into text.

- This setup is key for the voice interaction functionality of the robot. It forms the foundation upon which voice commands are
recognized and processed, enabling the robot to respond to user interactions in real time.
"""
def setup_and_load_model(args):
    # Access the arguments from the dictionary using square brackets
    samplerate = args['samplerate']
    blocksize = args['blocksize']
    device = args['device']
    dtype = args['dtype']
    channels = args['channels']
    callback = args['callback']

    # Assuming 'model' is defined elsewhere and accessible here
    # Create and return the RawInputStream and KaldiRecognizer objects
    return sd.RawInputStream(samplerate=samplerate, blocksize=blocksize, device=device, dtype=dtype, channels=channels, callback=callback), vosk.KaldiRecognizer(model, samplerate)

# Print startup messages
def print_startup_messages():
    logging.info('#' * 80)
    logging.info('Press Ctrl+C to stop the recording')
    logging.info('#' * 80)

def log_partial_result(recognizer):
    partial_result = recognizer.PartialResult()
    logging.info("Partial result: " + partial_result)

def dump_data_if_needed(data, dump_fn):
    if dump_fn is not None:
        with open(dump_fn, 'ab') as file:  # 'ab' mode for appending binary data
            file.write(data)

# Command mapping
commands = {
    'would you like to play hide and seek': play_hide_and_seek,
    'hide and seek': play_hide_and_seek,
    'can you play hide and seek with me': play_hide_and_seek,
    'who made you': respond_to_creator_inquiry,
    'who is your creator': respond_to_creator_inquiry,
    'who made you' : respond_to_creator_inquiry,
    'who is your builder' : respond_to_creator_inquiry,
    'do you sleep' : do_you_get_tired,
    'do you ever get tired' : do_you_get_tired,
    'you ever get tired' : do_you_get_tired,
    'what time is it' : current_time,
    'what is the current time' : current_time,
    'current time' : current_time,
    'what is the time' : current_time,
    'what is the current weather' : report_weather,
    'what is the weather' : report_weather,
    'what is the weather outside' : report_weather,
    'how is it looking outside' : report_weather,
    'what does the current weather' : report_weather,
    'take a picture' : take_picture_command,
    'take a photo' : take_picture_command,
    'take picture' : take_picture_command,
    'tell me a joke' : tell_joke,
    'tell a joke' : tell_joke,
    'can you tell me a good joke' : tell_joke,
    'got a good joke' : tell_joke,
    'do you joke at all' : tell_joke,
    'come to a joke' : tell_joke,
    'what is your favorite color' : favorite_color,
    'do you have a favorite color' : favorite_color,
    'what color do you like' : favorite_color,
    'what is the current temperature outside' : outside_temp,
    'how hot is it out' : outside_temp,
    'current temperature outside' : outside_temp,
    'what is the current temperature outside' : outside_temp,
    'what is the temperature outside' : outside_temp,
    # ... other commands ...
}

# Function to process the command
def process_command(final_phrase):
    """
        This function processes the recognized speech command. It takes the final phrase (result from speech recognition)
        and searches for predefined commands within the text. The function matches the spoken text against a dictionary of
        commands ('commands' dictionary). If a match is found, the corresponding function for the command is executed.
        If no predefined command is recognized, the function defaults to invoking the Chat GPT module ('run_chat_gpt4')
        to handle the query. This allows for a dynamic response capability where predefined commands are prioritized,
        and more open-ended queries are handled by Chat GPT.
    """
    text = final_phrase.get("text", "").lower()
    for phrase, func in commands.items():
        if phrase in text:
            func(final_phrase)
            return
    run_chat_gpt4(text)  # Default action if no command matches

def run_chat_gpt4(input_text):
    # Assuming you have a script or a command to run GPT-4 for processing input_text
    python37_path = '/usr/bin/python3.7'  # Replace with your Python 3.7 path
    script_path = 'chat_gpt4.py'  # Replace with the path to your chat_gpt4 script

    try:
        # Spawn a new process for chat_gpt4.py and pipe the input
        process = subprocess.Popen([python37_path, script_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = process.communicate(input=input_text)

        if stderr:
            logging.error("Error in chat_gpt4: " + stderr)
        else:
            # Process and maybe speak the output
            logging.info("GPT-4 responded: " + stdout)
            # speak(stdout)  # Uncomment if you have a speak function to vocalize the response
    except Exception as e:
        logging.error("Error occurred while running chat_gpt4: " + str(e))

def main():
    # Setup and model loading
    args = {
        'samplerate': 16000,  # Replace with actual samplerate value
        'blocksize': 8000,
        'device': 'default',  # Replace with actual device name
        'dtype': 'int16',
        'channels': 1,
        'callback': callback  # Ensure callback is defined elsewhere
    }

    # Pass the arguments dictionary to the setup function
    stream, rec = setup_and_load_model(args)

    with stream:
        print_startup_messages()

        while True:
            data = q.get()
            if not os.path.exists("speaking_semaphore.txt") and not is_speaking:
                if rec.AcceptWaveform(data):
                    final = rec.FinalResult()
                    final_phrase = json.loads(final)
                    process_command(final_phrase)
                else:
                    time.sleep(0.1)  # Prevent tight looping
                    log_partial_result(rec)
                    dump_data_if_needed(data, dump_fn)

try:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        '-l', '--list-devices', action='store_true',
        help='show list of audio devices and exit')
    args, remaining = parser.parse_known_args()
    if args.list_devices:
        logging.debug(sd.query_devices())
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
    args = parser.parse_args()
    parser.add_argument(
        '-r', '--samplerate', type=int, help='sampling rate')
    args = parser.parse_args(remaining)
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, 'input')
        args.samplerate = int(device_info['default_samplerate'])

    if args.filename:
        dump_fn = open(args.filename, "wb")
    else:
        dump_fn = None
    # Call the main function
    main()

except Exception as e:
    # Handle exceptions if necessary
    logging.error(f"Error occurred: {e}")
    sys.exit(1)

# exit on keyboard Interruptf
except KeyboardInterrupt:
    logging.info('\nDone')
    parser.exit(0)
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
