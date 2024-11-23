from chat_downloader import ChatDownloader
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import pandas as pd
import re

# Step 1: Initialize Sentiment Analysis Pipeline and Chatbot Model
sentiment_analyzer = pipeline("sentiment-analysis", framework="tf")
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

# Preprocess Messages (Handle Emojis)
def preprocess_message(text):
    """
    Preprocess chat messages to identify and handle non-standard emojis in the format :text:.
    Args:
        text (str): Original chat message
    Returns:
        str: Processed message
    """
    emoji_pattern = r":([a-zA-Z0-9_]+):"
    return re.sub(emoji_pattern, r"[EMOJI: \1]", text)

# Step 2: Fetch YouTube Comments
def fetch_chat_comments(url, max_comments=1000):
    """
    Fetch comments from a YouTube video using ChatDownloader.
    Args:
        url (str): URL of the YouTube video
        max_comments (int): Maximum number of comments to fetch
    Returns:
        list of dict: List of messages with timestamps and authors
    """
    chat = ChatDownloader().get_chat(url)
    comments = []
    for i, message in enumerate(chat):
        if i >= max_comments:
            break
        text = message.get("message", "")
        author_name = message.get("author", {}).get("name", "Anonymous")
        timestamp = message.get("time_in_seconds", None)

        # Preprocess text
        cleaned_text = preprocess_message(text)

        # Perform sentiment analysis
        sentiment = sentiment_analyzer(cleaned_text)[0]

        # Convert timestamp to minutes
        if timestamp is not None:
            minute = int(timestamp // 60)
        else:
            minute = "N/A"

        if text:
            comments.append({
                "minute": minute,
                "author_name": author_name,
                "text": cleaned_text,
                "sentiment": sentiment["label"],
                "score": sentiment["score"],
                "length": len(cleaned_text),  # Information density metric
                "unique_words": len(set(cleaned_text.split()))  # Another metric
            })
    return comments

# Step 3: Identify the Most Important Comment
def select_important_comments(comments):
    """
    Identify the most important comment per minute interval based on information density.
    Args:
        comments (list of dict): List of comments with metadata
    Returns:
        list of dict: Most important comment for each minute
    """
    df = pd.DataFrame(comments)
    df = df[df["minute"] != "N/A"]  # Filter out invalid timestamps

    # Define importance metric (e.g., longest comment, highest sentiment score)
    df["importance"] = df["length"] * df["unique_words"] * df["score"]

    # Select the most important comment per minute
    important_comments = df.loc[df.groupby("minute")["importance"].idxmax()].to_dict("records")
    return important_comments

# Step 4: Generate Responses
def generate_response(comment, sentiment):
    """
    Generate an intelligent response using DialoGPT.
    Args:
        comment (str): The user's comment
        sentiment (str): Sentiment label (POSITIVE, NEGATIVE, NEUTRAL)
    Returns:
        str: AI-generated response.
    """
    # Create the prompt
    prompt = f"The user said: {comment}. Sentiment: {sentiment}. Respond appropriately:"

    # Tokenize and generate response
    inputs = tokenizer.encode(prompt, return_tensors="pt")
    outputs = model.generate(inputs, max_length=100, num_return_sequences=1, pad_token_id=tokenizer.eos_token_id)

    # Decode and return only the response text
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

# Step 5: Main Script
if __name__ == "__main__":
    # YouTube video URL
    video_url = "https://www.youtube.com/watch?v=cOo10ndXtmk"

    # Fetch comments
    print("Fetching comments...")
    comments = fetch_chat_comments(video_url)

    # Select the most important comments per minute
    print("Selecting most important comments...")
    important_comments = select_important_comments(comments)

    # Generate and display responses
    print("\nMost Important Comments and AI Responses:")
    for comment in important_comments:
        response = generate_response(comment["text"], comment["sentiment"])
        print(f"Minute: {comment['minute']}")
        print(f"Author: {comment['author_name']} | Sentiment: {comment['sentiment']}")
        print(f"Comment: {comment['text']}")
        print(f"AI Reply: {response}")
        print("-" * 50)