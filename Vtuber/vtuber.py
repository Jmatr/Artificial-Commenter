import time
import multiprocessing
import redis
from openai import OpenAI
import requests
from dotenv import load_dotenv
import os
import ast
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Load personality
personality_file = "personality.txt"

# Initialize OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found. Set the OPENAI_API_KEY environment variable.")

# Initialize OpenAI Client
client = OpenAI(api_key=api_key)

# Connect to Redis
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,
)

TTS_SERVICE_URL = "http://localhost:5000/synthesize"

def load_personality(filename):
    """
    Loads the streamer personality from a text file.
    """
    personality = {}
    try:
        with open(filename, "r") as file:
            for line in file:
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip().lower()
                    value = value.strip()
                    if "," in value:  # Convert comma-separated values into a list
                        value = [v.strip() for v in value.split(",")]
                    personality[key] = value
    except FileNotFoundError:
        print(f"Error: Personality file '{filename}' not found.")
        exit(1)
    except Exception as e:
        print(f"Error loading personality file: {e}")
        exit(1)
    return personality

streamer_personality = load_personality(personality_file)

def generate_ai_response(content, personality, memory):
    """
    Generates an AI response using OpenAI GPT model, incorporating past interactions.
    """
    memory_messages = [{"role": "assistant", "content": m} for m in memory]
    messages = [
        {"role": "system", "content": f"""
        You are {personality['name']}, a virtual streamer with the following personality:
        - Background: {personality['background']}
        - Favorites: {', '.join(personality['favorites'])}
        - Dislikes: {', '.join(personality['dislikes'])}

        {personality['prompt']}
        """},
        {"role": "user", "content": content},
    ]
    messages = memory_messages + messages

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=300,
        temperature=0.4,
    )
    return response.choices[0].message.content.strip()

def speak_response(response):
    """
    Sends the response text to the TTS service.
    """
    try:
        res = requests.post(TTS_SERVICE_URL, json={"text": response})
        if res.status_code == 200:
            result = res.json()
            if result["status"] == "success":
                print("Speech synthesized successfully.")
            else:
                print(f"Error synthesizing speech: {result['message']}")
        else:
            print(f"TTS service error: {res.text}")
    except Exception as e:
        print(f"Error calling TTS service: {str(e)}")

def fetch_user_input(user_pool):
    """
    Fetches user input from the Redis queue.
    """
    while True:
        user_input = redis_client.rpop("user_input_queue")
        if user_input:
            user_pool.append(user_input)
        time.sleep(1)

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
            comment["timestamp"] = datetime.now()  # Add timestamp
            print(f"Received comment: {comment}")
            comment_pool.append(comment)

def clean_comment_pool(comment_pool, interval=30):
    """
    Periodically removes comments older than 2 minutes from the comment pool.
    """
    while True:
        time.sleep(interval)
        now = datetime.now()
        comment_pool[:] = [c for c in comment_pool if now - c["timestamp"] <= timedelta(minutes=2)]
        print(f"Cleaned comment pool. Remaining comments: {len(comment_pool)}")

def responder(user_pool, comment_pool, memory):
    """
    Virtual streamer responds based on user input, viewer comments, or generates random thoughts.
    """
    while True:
        time.sleep(1)

        if user_pool:
            user_input = user_pool.pop(0)
            response = generate_ai_response(user_input, streamer_personality, memory)
            print(f"Aelina says (to user): {response}")
            speak_response(response)
            memory.append(f"User: {user_input}\nAelina: {response}")
        elif comment_pool:
            top_comment = max(comment_pool, key=lambda c: c["likes"])
            response = generate_ai_response(top_comment["text"], streamer_personality, memory)
            print(f"Aelina says (to comment): {response}")
            speak_response(response)
            comment_pool.remove(top_comment)
            memory.append(f"Comment: {top_comment['text']}\nAelina: {response}")
        else:
            response = generate_ai_response("Say something random and interesting! Think what streamer will do to heatup the stream. Be within 4 sentences.", streamer_personality, memory)
            print(f"Aelina says (random thought): {response}")
            speak_response(response)
            memory.append(f"Aelina (random): {response}")

        if len(memory) > 10:
            memory.pop(0)

if __name__ == "__main__":
    # Load streamer personality from file
    # streamer_personality = load_personality(personality_file)

    comment_pool = multiprocessing.Manager().list()
    user_pool = multiprocessing.Manager().list()
    memory = multiprocessing.Manager().list()

    # Fetch user input from Redis
    input_process = multiprocessing.Process(target=fetch_user_input, args=(user_pool,))
    comment_process = multiprocessing.Process(target=subscribe_to_comments, args=(comment_pool,))
    responder_process = multiprocessing.Process(target=responder, args=(user_pool, comment_pool, memory))
    cleanup_process = multiprocessing.Process(target=clean_comment_pool, args=(comment_pool,))

    # Start processes
    input_process.start()
    comment_process.start()
    responder_process.start()
    cleanup_process.start()

    # Keep main process alive
    input_process.join()
    comment_process.join()
    responder_process.join()
    cleanup_process.start()