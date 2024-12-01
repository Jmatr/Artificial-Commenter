import time
import multiprocessing
import redis
from openai import OpenAI
import pyttsx3
import ast  # To safely parse stringified dictionaries
from speech_recognition import Recognizer, Microphone, WaitTimeoutError, UnknownValueError, RequestError
from dotenv import load_dotenv
import os

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

# Connect to Redis
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

# Define streamer's personality
streamer_personality = {
    "name": "Luna",
    "background": "A cheerful AI streamer who loves space exploration and sci-fi.",
    "favorites": ["stars", "video games", "blue color", "cats"],
    "dislikes": ["spam comments", "negative vibes"]
}


def generate_ai_response(content, personality, memory):
    """
    Generates an AI response using OpenAI GPT model, incorporating past interactions.
    """
    # Include memory in the conversation context
    memory_messages = [{"role": "assistant", "content": m} for m in memory]
    messages = [
        {"role": "system", "content": f"""
        You are {personality['name']}, a virtual streamer with the following personality:
        - Background: {personality['background']}
        - Favorites: {', '.join(personality['favorites'])}
        - Dislikes: {', '.join(personality['dislikes'])}

        Respond thoughtfully and creatively. Start with first person, no need with words like absolutely or sure thing
        . Luna says: is just the format to show you the previous conversation
        """},
        {"role": "user", "content": f"{content}"}
    ]

    # Combine memory and new messages
    messages = memory_messages + messages

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=200,
        temperature=0.5
    )

    return response.choices[0].message.content.strip()

def speak_response(response):
    """
    Speaks the AI-generated response using pyttsx3.
    """
    tts_engine.say(response)
    tts_engine.runAndWait()

def subscribe_to_comments(comment_pool):
    """
    Subscribes to the Redis channel to receive and store comments in the comment pool.
    """
    pubsub = redis_client.pubsub()
    pubsub.subscribe("comment_channel")
    print("Subscribed to comment channel...")

    for message in pubsub.listen():
        if message["type"] == "message":
            comment = ast.literal_eval(message["data"])  # Safely parse stringified dict
            print(f"Received comment: {comment}")
            comment_pool.append(comment)

def listen_to_user(user_pool):
    """
    Listens for user input via speech and adds it to the user pool.
    """
    recognizer = Recognizer()
    while True:
        try:
            with Microphone() as source:
                print("Listening for user input... (Say 'Hi Luna')")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=5)
                user_input = recognizer.recognize_google(audio)

                if "hi luna" in user_input.lower():
                    print(f"User said: {user_input}")
                    user_pool.append(user_input)
        except WaitTimeoutError:
            continue
        except UnknownValueError:
            print("Could not understand the user.")
        except RequestError:
            print("Speech recognition service unavailable.")

def luna_responder(user_pool, comment_pool, memory):
    """
    Luna responds based on user input, viewer comments, or generates random thoughts.
    """
    while True:
        time.sleep(5)  # Process every 5 seconds

        if user_pool:
            # Respond to user input
            user_input = user_pool.pop(0)
            response = generate_ai_response(user_input, streamer_personality, memory)
            print(f"Luna says (to user): {response}")
            speak_response(response)
            memory.append(f"User: {user_input}\nLuna: {response}")
        elif comment_pool:
            # Respond to most liked comment
            top_comment = max(comment_pool, key=lambda c: c["likes"])
            response = generate_ai_response(top_comment["text"], streamer_personality, memory)
            print(f"Luna says (to comment): {response}")
            speak_response(response)
            comment_pool.remove(top_comment)
            memory.append(f"Comment: {top_comment['text']}\nLuna: {response}")
        else:
            # Generate random thought
            response = generate_ai_response("Generate something interesting! No need to start with absolutely or"
                                            " sure thing. Be concise with around 100 words", streamer_personality, memory)
            print(f"Luna says (random thought): {response}")
            speak_response(response)
            memory.append(f"Luna: {response}")

        # Prune memory if it exceeds a certain size
        if len(memory) > 10:
            memory.pop(0)

if __name__ == "__main__":
    # Create shared resources
    comment_pool = multiprocessing.Manager().list()
    user_pool = multiprocessing.Manager().list()
    # Memory for past interactions
    memory = multiprocessing.Manager().list()

    # Set up processes
    comment_process = multiprocessing.Process(target=subscribe_to_comments, args=(comment_pool,))
    user_process = multiprocessing.Process(target=listen_to_user, args=(user_pool,))
    responder_process = multiprocessing.Process(target=luna_responder, args=(user_pool, comment_pool, memory))

    # Start processes
    comment_process.start()
    user_process.start()
    responder_process.start()

    # Keep main process alive
    comment_process.join()
    user_process.join()
    responder_process.join()

