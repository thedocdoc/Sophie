import openai
import pyttsx3
import sys
import time

# Initialize the pyttsx3 engine
engine = pyttsx3.init()

# Set the speech rate
engine.setProperty('rate', 110)  # Adjust this value to change speed

is_speaking = False

# Load your OpenAI API key
openai.api_key = 'your_api_key'

# Initialize text-to-speech engine
engine = pyttsx3.init()

def ask_gpt(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message}
            ]
        )
        answer = response['choices'][0]['message']['content']
        return answer
    except Exception as e:
        return f"An error occurred: {e}"

def monitor_speech(engine):
    global is_speaking
    while engine.isBusy():
        time.sleep(0.1)
    is_speaking = False

def speak(text):
    global is_speaking
    time.sleep(0.8)  # Short delay before starting speech
    is_speaking = True
    engine.say(text)
    engine.runAndWait()
    time.sleep(len(text) * 0.01)  # Delay after speech
    is_speaking = False

def main():
    if sys.stdin.isatty():
        # Interactive mode: input comes from the user typing
        while True:
            message = input("Ask something: ")
            if message.lower() == "exit":
                break
            answer = ask_gpt(message)
            print(f"Answer: {answer}")
            speak(answer)  # Using pyttsx3 for text-to-speech
    else:
        # Non-interactive mode: input is piped from another process
        for message in sys.stdin:
            message = message.strip()
            if message.lower() == "exit":
                break
            answer = ask_gpt(message)
            print(f"Answer: {answer}")
            speak(answer)  # Using pyttsx3 for text-to-speech

if __name__ == "__main__":
    main()
