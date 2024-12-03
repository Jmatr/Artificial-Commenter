
# Aelina (星依) - Virtual Streamer Project

Aelina (星依) is an innovative virtual streamer concept, designed to engage with audiences through a dynamic and consistent personality. This project leverages cutting-edge technologies, including natural language processing, comment interaction systems, and text-to-speech synthesis, to create a unique and immersive viewer experience.

## Project Overview

Aelina is a star explorer with white hair, wearing gothic lolita attire, and embodying a mysterious aura. She interacts with her audience by responding to the most relevant comments, expressing her distinct personality through intelligent and lifelike dialogue.

### Key Features
- **Comment Interaction**: Responds to top comments in 30-second intervals.
- **Dynamic Personality**: A consistent character with a backstory, likes, and dislikes.
- **Idle Conversations**: Fills silent moments with random but relevant musings.
- **Bilingual Support**: Suitable for English and Chinese audiences.

### Technologies Used
1. **OpenAI GPT**: For generating natural language responses.
2. **Redis**: To manage the comment pool and prioritize interactions.
3. **Speech Recognizer**: Captures user input during live streams.
4. **Text-to-Speech (TTS)**: Converts responses into a lifelike voice.
5. **Python Multiprocessing**: Ensures smooth handling of parallel tasks.

## Project Architecture

The system is built with modular components to handle different aspects of the streamer's functionality:
1. **Comment Handler**: Processes and ranks incoming comments based on relevance.
2. **Response Generator**: Generates thoughtful, character-appropriate replies using OpenAI GPT.
3. **Voice Synthesizer**: Converts textual responses into speech with a unique voice tone.
4. **Idle System**: Ensures continuous engagement even during lulls in interaction.
5. **Language Support**: Allows seamless integration of English and Chinese dialogue.

## Future Enhancements
- **Emotion Detection**: Enable Aelina to adapt tone and responses based on the mood of the comments.
- **Advanced Animation**: Integrate real-time facial expressions and gestures.
- **Content Customization**: Allow the audience to shape Aelina’s adventures and personality.
- **Streaming Integration**: Direct integration with popular platforms like Twitch and Bilibili.

## Installation and Setup

### Prerequisites
- Python 3.9 or later
- Redis Server
- OpenAI API key
- TTS Service API key

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/Jmatr/Artificial-Commenter
   cd aelina-virtual-streamer
   ```
2. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the Redis server:
   ```bash
   redis-server
   ```
4. Run the main script:
   ```bash
   python main.py
   ```

### References
- [Stack Overflow: Live Chat Replay Log History for YouTube Streaming](https://stackoverflow.com/questions/55789448/is-there-any-way-to-get-the-live-chat-replay-log-history-for-youtube-streaming-v)
- [Redis Installation Guide for Windows 11](https://redis.io/blog/install-redis-windows-11/)

## Contributing

Contributions are welcome! Please submit a pull request with a clear description of your changes or reach out via issues for feature requests or bug reports.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
