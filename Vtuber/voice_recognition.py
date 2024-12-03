import os
import time
import redis
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

# Load environment variables
load_dotenv()

# Redis setup
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,
)

# Azure Speech SDK setup
speech_key = os.getenv("AZURE_API_KEY")
service_region = os.getenv("AZURE_API_REGION")

if not speech_key or not service_region:
    raise ValueError("Azure Speech SDK key or region not found. Set AZURE_SPEECH_KEY and AZURE_REGION in the environment.")

# Configure Azure Speech Recognizer
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

# Enable semantic segmentation for improved transcription
speech_config.set_property(speechsdk.PropertyId.Speech_SegmentationStrategy, "Semantic")

# Enable language auto-detection (for example, English and Spanish)
speech_config.speech_recognition_language = "en-US"  # Default language
auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
    languages=["en-US", "zh-CN"]
)

# Continuous recognition function
def continuous_recognition():
    """
    Performs continuous recognition with Azure Speech SDK and publishes results to Redis.
    """
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_config.set_service_property(
        name="Microsoft.Audio.NoiseSuppression",
        value="High",
        channel=speechsdk.ServicePropertyChannel.UriQueryParameter,
    )
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        auto_detect_source_language_config=auto_detect_source_language_config,
        audio_config=audio_config,
    )

    # Variable to track recognition state
    done = False

    # Callback functions
    def recognizing_cb(evt):
        print(f"RECOGNIZING: {evt.result.text}")

    def recognized_cb(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print(f"RECOGNIZED: {evt.result.text}")
            detected_language = evt.result.properties[
                speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult
            ]
            print(f"Detected Language: {detected_language}")

            # Publish recognized text to Redis
            redis_client.lpush("user_input_queue", evt.result.text)

        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized.")

    def session_started_cb(evt):
        print("SESSION STARTED")

    def session_stopped_cb(evt):
        print("SESSION STOPPED")
        nonlocal done
        done = True

    def canceled_cb(evt):
        print(f"CANCELED: {evt}")
        nonlocal done
        done = True

    # Connect callbacks
    speech_recognizer.recognizing.connect(recognizing_cb)
    speech_recognizer.recognized.connect(recognized_cb)
    speech_recognizer.session_started.connect(session_started_cb)
    speech_recognizer.session_stopped.connect(session_stopped_cb)
    speech_recognizer.canceled.connect(canceled_cb)

    # Start continuous recognition
    speech_recognizer.start_continuous_recognition()
    print("Starting continuous recognition. Speak into the microphone...")

    # Keep recognition running
    while not done:
        time.sleep(0.5)

    # Stop recognition
    speech_recognizer.stop_continuous_recognition()

if __name__ == "__main__":
    print("Starting Azure continuous voice recognition...")
    continuous_recognition()