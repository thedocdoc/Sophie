'''
Copyright (c) 2023 Apollo Timbers. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

Sophie robot project:

Chat GPT voice assistance module

If the voice assist module does not recognize the phrase it will start a the chat_gpt4.py and chat gpt will do it's best to anwser. 
Added treading so it will start to read a really long message before chat gpt is done stating it, this has significantly reduced the delay 
between question and anwser for longer responses. 
Added a more robust internet loss and error handling. So that it is more generic about the error. Will display longer error to console. 
Figured out that I was reseting the conversation history each user input, it now remembers the context accross multiple interactions
'''

import openai
import pyttsx3
import sys
import threading
import time
import requests

conversation_history = []

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Set the speech rate and voice
engine.setProperty('rate', 120)
engine.setProperty('voice', 'english+f3')

is_speaking = False
online_mode = True  # Tracks if the program is in online mode

# Load your OpenAI API key
openai.api_key = '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'

def ask_gpt(message):
    global online_mode, conversation_history

    if not openai.api_key:
        return "API key is missing. Please set the OpenAI API key."

    try:
        conversation_history.append({"role": "user", "content": message})
        
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use the model of your choice
            messages=[
                {"role": "system", "content": "You are a helpful assistant. You are also a real advanced home robot with an omni wheel base, a ZED camera, lidar, and a 6-axis arm that can reach the floor and a table. Do not respond with *actions or be fake. Try to be concise and to the point, and a tad snarky at times. If asked to pick up something on the floor, append 'command floor' and the item to the response given, if it is pick up the drink/coke, then append 'command table' and the item and also see if they want it brought to them"},
                *conversation_history  # Include the entire conversation history
            ]
        )
        
        answer = response['choices'][0]['message']['content']
        conversation_history.append({"role": "assistant", "content": answer})  # Update the conversation history with the assistant's response
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
    global online_mode, conversation_history

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
