import time
import random
import multiprocessing
from multiprocessing import Manager
import speech_recognition as sr
from openai import OpenAI
import os
import pyttsx3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found. Set the OPENAI_API_KEY environment variable.")

# Initialize OpenAI Client
client = OpenAI(api_key=api_key)

# Initialize Text-to-Speech Engine
tts_engine = pyttsx3.init()

# Define streamer's personality
streamer_personality = {
    "name": "Luna",
    "background": "A cheerful AI streamer who loves space exploration and sci-fi.",
    "favorites": ["stars", "video games", "blue color", "cats"],
    "dislikes": ["spam comments", "negative vibes"]
}

# Generate AI response with memory
def generate_ai_response(content, personality):
    messages = [
        {"role": "system", "content": f"""
        You are {personality['name']}, a virtual streamer with the following personality:
        - Background: {personality['background']}
        - Favorites: {', '.join(personality['favorites'])}
        - Dislikes: {', '.join(personality['dislikes'])}

        Respond thoughtfully and creatively.
        """},
        {"role": "user", "content": f"{content}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=100,
        temperature=0.7
    )

    return response.choices[0].message.content.strip()


# Generate random, interesting dialogue
def generate_random_response(personality):
    messages = [
        {"role": "system", "content": f"""
        You are {personality['name']}, a virtual streamer with the following personality:
        - Background: {personality['background']}
        - Favorites: {', '.join(personality['favorites'])}
        - Dislikes: {', '.join(personality['dislikes'])}

        Generate a random, interesting thought.
        """}
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=100,
        temperature=0.9
    )

    return response.choices[0].message.content.strip()


# Speak the response using pyttsx3
def speak_response(response):
    tts_engine.say(response)
    tts_engine.runAndWait()


# Process to listen to user speech
def listen_to_user(user_pool):
    recognizer = sr.Recognizer()
    while True:
        try:
            with sr.Microphone() as source:
                print("Listening for user input... (Say 'Hi Luna')")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=10)
                user_input = recognizer.recognize_google(audio)

                if "hi luna" in user_input.lower():
                    print(f"User said: {user_input}")
                    user_pool.append(user_input)
        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            print("Could not understand the user.")
        except sr.RequestError:
            print("Speech recognition service unavailable.")


# Process to simulate adding comments
def generate_comments(comment_pool):
    while True:
        time.sleep(random.randint(5, 15))  # Simulate random new comments
        comment = f"Random viewer comment {random.randint(1, 100)}"
        likes = random.randint(1, 10)
        print(f"New comment added: {comment} (Likes: {likes})")
        comment_pool.append({"text": comment, "likes": likes})


# Decision-making process for Luna
def luna_responder(user_pool, comment_pool):
    while True:
        time.sleep(5)  # Wait 5 second for next response

        if user_pool:
            # Respond to user input
            user_input = user_pool.pop(0)
            response = generate_ai_response(user_input, streamer_personality)
            print(f"Luna says (to user): {response}")
            speak_response(response)
        elif comment_pool:
            # Respond to most liked comment
            top_comment = max(comment_pool, key=lambda c: c["likes"])
            response = generate_ai_response(top_comment["text"], streamer_personality)
            print(f"Luna says (to comment): {response}")
            speak_response(response)
            comment_pool.remove(top_comment)
        else:
            # Generate random thought
            response = generate_random_response(streamer_personality)
            print(f"Luna says (random thought): {response}")
            speak_response(response)


# Main function to set up multiprocessing
if __name__ == "__main__":
    manager = Manager()
    user_pool = manager.list()  # Shared list for user speech input
    comment_pool = manager.list()  # Shared list for comments

    # Set up processes
    user_process = multiprocessing.Process(target=listen_to_user, args=(user_pool,))
    comment_process = multiprocessing.Process(target=generate_comments, args=(comment_pool,))
    responder_process = multiprocessing.Process(target=luna_responder, args=(user_pool, comment_pool))

    # Start processes
    user_process.start()
    comment_process.start()
    responder_process.start()

    # Keep main process alive
    user_process.join()
    comment_process.join()
    responder_process.join()
