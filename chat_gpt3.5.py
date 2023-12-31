'''
Copyright (c) 2022 Apollo Timbers. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

Sophie robot project:

Offline and chat gpt voice assistance module

This openly listens to it's surroundings with the Vosk api, when a key phrase is spoken it then responds with the festival text to speech generator.
Built in weather system to pull in local weather, This uses the openweather API to request current weather conditions. If it does not recognize the
phrase it will start a the chat_gpt3.5.py and chat gpt will do it's best to anwser. Added a way for it to gracfully handle internet outages and inform the user.
Needs cleaning I think I got voice assit to handle internt issues
'''

import openai
import pyttsx3
import sys
import time
import socket

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Set the speech rate
engine.setProperty('rate', 120)  # Adjust this value to change speed

# Set to a female voice
engine.setProperty('voice', 'english+f3')

is_speaking = False
last_internet_loss_announcement = 0  # Time of last internet loss announcement

# Load your OpenAI API key
openai.api_key = 'you_api_key'  # Replace with your actual API key

def is_connected():
    try:
        socket.create_connection(("8.8.8.8", 53))
        return True
    except OSError:
        pass
    return False

def ask_gpt(message):
    global last_internet_loss_announcement
    if not is_connected():
        current_time = time.time()
        if current_time - last_internet_loss_announcement > 60:  # 60 seconds before repeating message
            last_internet_loss_announcement = current_time
            return "   ", True  #Internet connection lost. Switching to offline mode.
        return "", False  # Do not repeat the message if within timeout

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Try to be concise and to the point, and a tad snarky at times"},
                {"role": "user", "content": message}
            ]
        )
        answer = response['choices'][0]['message']['content']
        return answer, False
    except Exception as e:
        return f"An error occurred: {e}", False

def speak(text, longer_sleep=False):
    global is_speaking
    if text:  # Only proceed if there is text to speak
        time.sleep(0.8)  # Short delay before starting speech
        is_speaking = True
        engine.say(text)
        engine.runAndWait()
        sleep_duration = len(text) * 0.015  # Adjusted duration
        if longer_sleep:
            sleep_duration += 3  # Additional delay for internet error message
        time.sleep(sleep_duration)  # Delay after speech
        is_speaking = False

def main():
    if sys.stdin.isatty():
        while True:
            if is_speaking:
                continue  # Skip processing input while speaking

            message = input("Ask something: ")
            if message.lower() == "exit":
                break
            answer, longer_sleep = ask_gpt(message)
            if answer:  # Only print and speak if there is an answer
                print(f"Answer: {answer}")
                speak(answer, longer_sleep)
    else:
        for message in sys.stdin:
            if is_speaking:
                continue

            message = message.strip()
            if message.lower() == "exit":
                break
            answer, longer_sleep = ask_gpt(message)
            if answer:
                print(f"Answer: {answer}")
                speak(answer, longer_sleep)

if __name__ == "__main__":
    main()
