import time
import random
import redis

# Connect to Redis
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

def extract_comments():
    """
    Simulates extracting comments from a streaming platform
    and publishing them to a Redis channel.
    """
    while True:
        # Simulate a new comment
        comment = {
            "text": f"Viewer comment something interesting {random.randint(1, 100)}",
            "likes": random.randint(1, 10),
        }

        # Publish to Redis channel
        redis_client.publish("comment_channel", str(comment))
        print(f"Published comment: {comment}")

        # Simulate delay between new comments
        time.sleep(random.randint(5, 15))

if __name__ == "__main__":
    print("Starting comment extraction...")
    extract_comments()