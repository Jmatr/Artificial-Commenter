import redis
from speech_recognition import Recognizer, Microphone, WaitTimeoutError, UnknownValueError, RequestError

# Connect to Redis
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,
)

def listen_and_publish():
    """
    Listens for user input via speech and publishes recognized text to Redis.
    """
    recognizer = Recognizer()
    while True:
        try:
            with Microphone() as source:
                print("Listening for user input...")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=5)
                user_input = recognizer.recognize_google(audio)
                print(f"User said: {user_input}")
                redis_client.lpush("user_input_queue", user_input)
        except WaitTimeoutError:
            continue
        except UnknownValueError:
            print("Could not understand the user.")
        except RequestError:
            print("Speech recognition service unavailable.")

if __name__ == "__main__":
    print("Starting voice recognition...")
    listen_and_publish()
