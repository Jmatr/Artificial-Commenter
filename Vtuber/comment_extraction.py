import time
import random
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found. Set the OPENAI_API_KEY environment variable.")

# Initialize OpenAI Client
client = OpenAI(api_key=api_key)

# Define streamer's personality
streamer_personality = {
    "name": "Luna",
    "background": "A cheerful AI streamer who loves space exploration and sci-fi.",
    "favorites": ["stars", "video games", "blue color", "cats"],
    "dislikes": ["spam comments", "negative vibes"]
}

# Simulate a comment section (replace this with real data in a live system)
comments = [
    {"text": "What's your favorite sci-fi movie?", "likes": 5, "timestamp": time.time()},
    {"text": "I love space too!", "likes": 3, "timestamp": time.time()},
    {"text": "Just dropping by to say hi!", "likes": 1, "timestamp": time.time()}
]

# Memory to store past interactions
memory = []
MAX_MEMORY = 10  # Limit memory to the last 10 interactions


# Function to determine the most important comment
def get_most_important_comment(comments):
    if not comments:
        return None
    return max(comments, key=lambda c: c["likes"])


# Generate AI response using memory
def generate_ai_response(comment, personality, memory):
    # Build memory into the message
    memory_messages = [{"role": "assistant", "content": mem} for mem in memory]

    # System and user prompt
    messages = [
        {"role": "system", "content": f"""
        You are {personality['name']}, a virtual streamer with the following personality:
        - Background: {personality['background']}
        - Favorites: {', '.join(personality['favorites'])}
        - Dislikes: {', '.join(personality['dislikes'])}

        Respond thoughtfully, referencing past interactions when appropriate.
        """},
        {"role": "user", "content": f"A viewer commented: \"{comment}\""}
    ]

    # Combine memory and new messages
    messages = memory_messages + messages

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=100,
        temperature=0.7
    )

    return response.choices[0].message.content.strip()


# Generate random responses dynamically
def generate_random_response(personality):
    """Generate a random, interesting response using OpenAI."""
    messages = [
        {"role": "system", "content": f"""
        You are {personality['name']}, a virtual streamer with the following personality:
        - Background: {personality['background']}
        - Favorites: {', '.join(personality['favorites'])}
        - Dislikes: {', '.join(personality['dislikes'])}

        Generate a random and interesting thought or comment to share with viewers.
        """}
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=100,
        temperature=0.9  # Higher temperature for creativity
    )

    return response.choices[0].message.content.strip()


# Main loop for the virtual streamer
def streamer_loop():
    last_response_time = time.time()

    while True:
        current_time = time.time()
        if current_time - last_response_time >= 30:  # Check if 30 seconds have passed
            important_comment = get_most_important_comment(comments)

            if important_comment:
                ai_response = generate_ai_response(important_comment["text"], streamer_personality, memory)
                print(f"Luna says: {ai_response}")

                # Add response to memory
                memory.append(ai_response)
                if len(memory) > MAX_MEMORY:
                    memory.pop(0)  # Maintain memory limit

                # Remove the handled comment
                comments.remove(important_comment)
            else:
                random_response = generate_random_response(streamer_personality)
                print(f"Luna says: {random_response}")

                # Add random response to memory
                memory.append(random_response)
                if len(memory) > MAX_MEMORY:
                    memory.pop(0)

            last_response_time = current_time

        time.sleep(1)  # Avoid CPU overuse in the loop


# Run the streamer
streamer_loop()
