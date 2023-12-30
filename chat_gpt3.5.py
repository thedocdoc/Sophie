import openai
import pyttsx3
import sys
import os # import os (used to control festival tts)

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

def speak(text):
    engine.say(text)
    engine.runAndWait()

def main():
    if sys.stdin.isatty():
        # Interactive mode: input comes from the user typing
        while True:
            message = input("Ask something: ")
            if message.lower() == "exit":
                break
            answer = ask_gpt(message)
            print(f"Answer: {answer}")
            os.popen('echo "{0}" | festival -b --tts'.format(answer))
    else:
        # Non-interactive mode: input is piped from another process
        for message in sys.stdin:
            message = message.strip()
            if message.lower() == "exit":
                break
            answer = ask_gpt(message)
            print(f"Answer: {answer}")
            os.popen('echo "{0}" | festival -b --tts'.format(answer))

if __name__ == "__main__":
    main()
