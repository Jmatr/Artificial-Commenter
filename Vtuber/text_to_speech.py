import azure.cognitiveservices.speech as speechsdk
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize Flask App
app = Flask(__name__)

# Configure Azure Speech SDK
speech_key = os.getenv("AZURE_API_KEY")
service_region = os.getenv("AZURE_API_REGION")
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_config.speech_synthesis_voice_name = "en-US-EvelynMultilingualNeural"  # Replace with desired voice

def synthesize_speech(text):
    """
    Synthesizes speech from text using Azure Speech SDK.
    """
    try:
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        result = speech_synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return {"status": "success", "message": "Speech synthesized successfully"}
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            return {
                "status": "error",
                "message": f"Speech synthesis canceled: {cancellation_details.reason}",
                "details": cancellation_details.error_details,
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route("/synthesize", methods=["POST"])
def synthesize():
    """
    Endpoint to synthesize speech.
    Expects JSON with a 'text' field.
    """
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"status": "error", "message": "No text provided"}), 400

    response = synthesize_speech(data["text"])
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)