'''
Copyright (c) 2023 Apollo Timbers. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

Sophie robot project:

Chat GPT voice assistance module

If the voice assist module does not recognize the phrase it will start a the chat_gpt3.5.py and chat gpt will do it's best to anwser. 
Added a way for it to gracfully handle internet outages and inform the user.
Added treading so it will start to read a really long message before chat gpt is done stating it, this has significantly reduced the delay 
between question and anwser for longer responses. 
'''

import openai
import pyttsx3
import sys
import threading
import time
import requests

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Set the speech rate and voice
engine.setProperty('rate', 120)
engine.setProperty('voice', 'english+f3')

is_speaking = False
online_mode = True  # Tracks if the program is in online mode

# Load your OpenAI API key
openai.api_key = 'your_api_key'

def ask_gpt(message):
    global online_mode

    if not openai.api_key:
        return "API key is missing. Please set the OpenAI API key."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Try to be concise and to the point, and a tad snarky at times."},
                {"role": "user", "content": message}
            ]
        )
        answer = response['choices'][0]['message']['content']
        return answer
    except requests.exceptions.ConnectionError:
        online_mode = False
        return "Offline mode only due to internet loss."
    except openai.error.AuthenticationError:
        return "Authentication failed. Please check your OpenAI API key."
    except Exception as e:
        print(f"Error: {e}")  # Log the specific error
        return "An error occurred. Please try again later."

def speak(text):
    def run_speak():
        global is_speaking
        is_speaking = True
        engine.say(text)
        engine.runAndWait()
        is_speaking = False

    threading.Thread(target=run_speak).start()

def main():
    global online_mode
    if sys.stdin.isatty():
        while True:
            message = input("Ask something: ")
            if message.lower() == "exit":
                break
            answer = ask_gpt(message)
            print(f"Answer: {answer}")
            speak(answer)
    else:
        for message in sys.stdin:
            message = message.strip()
            if message.lower() == "exit":
                break
            answer = ask_gpt(message)
            print(f"Answer: {answer}")
            speak(answer)

if __name__ == "__main__":
    main()
