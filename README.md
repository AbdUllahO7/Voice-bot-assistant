# 🍔 Joe's Restaurant - AI Voice Ordering System

A professional voice-enabled restaurant ordering system with advanced natural language processing, built with Python, Google Cloud Speech/TTS, and OpenAI GPT integration.



## ✨ Features

### 🎤 Advanced Voice Recognition
- **Google Cloud Speech-to-Text** integration for accurate voice recognition
- **Natural conversation flow** with context awareness
- **Noise handling** and confidence scoring
- **Multi-language support** (configurable)

### 🧠 AI-Powered Understanding
- **GPT Integration** for natural language understanding
- **Complex command parsing**: "Remove the coca-cola and add two fries instead"
- **Smart quantity detection**: "I want three burgers"
- **Context-aware responses** and recommendations

### 🖥️ Professional UI
- **Modern, responsive design** with professional styling
- **Real-time order updates** with quantity grouping
- **Touch-friendly interface** for non-voice interactions
- **Conversation logging** and status indicators

### 🛒 Smart Ordering Features
- **Quantity handling**: Voice commands like "two burgers" or "three sodas"
- **Order modifications**: "Remove the burger", "Cancel my fries"
- **Intelligent recommendations** based on order history
- **Order persistence** with detailed JSON logging

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Google Cloud Account** (for Speech & TTS APIs)
- **OpenAI Account** (for GPT integration)
- **Microphone** for voice input
- **Speakers** for voice output

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/voice-restaurant-system.git
   cd voice-restaurant-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up configuration**
   ```bash
   cp config_template.py config.py
   ```

4. **Configure API keys** (see [Configuration](#configuration) section)

5. **Run the application**
   ```bash
   python whisper_voice_bot.py
   ```

## ⚙️ Configuration

### 1. Google Cloud Setup

1. **Create a Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable APIs**
   ```bash
   # Enable required APIs
   gcloud services enable speech.googleapis.com
   gcloud services enable texttospeech.googleapis.com
   ```

3. **Create Service Account**
   - Go to IAM & Admin → Service Accounts
   - Create new service account with Speech API permissions
   - Download JSON key file

4. **Update config.py**
   ```python
   GOOGLE_CLOUD_SERVICE_ACCOUNT_PATH = "/path/to/your/service-account-key.json"
   ```

### 2. OpenAI Setup

1. **Get API Key**
   - Visit [OpenAI Platform](https://platform.openai.com/api-keys)
   - Create new API key
   - Add credits to your account

2. **Update config.py**
   ```python
   OPENAI_API_KEY = "sk-your-api-key-here"
   ```

### 3. Configuration Options

```python
# config.py - Full configuration example

# API Keys
OPENAI_API_KEY = "sk-your-openai-key"
GOOGLE_CLOUD_SERVICE_ACCOUNT_PATH = "/path/to/service-account.json"

# Voice Settings
VOICE_ENABLED = True
TTS_VOICE_NAME = "en-US-Neural2-F"  # Female neural voice
TTS_SPEAKING_RATE = 0.95           # Slower = more clear
TTS_LANGUAGE_CODE = "en-US"

# Audio Settings
AUDIO_CHUNK_SIZE = 4096            # Larger = better quality
AUDIO_SAMPLE_RATE = 16000          # Standard rate
AUDIO_RECORD_SECONDS = 5           # Listening window
CONFIDENCE_THRESHOLD = 0.7         # Speech recognition accuracy

# App Settings
RESTAURANT_NAME = "Joe's Restaurant"
AUTO_START_VOICE = True
SAVE_ORDERS = True
```

## 📋 Dependencies

Create a `requirements.txt` file:

```text
google-cloud-speech>=2.21.0
google-cloud-texttospeech>=2.14.1
openai>=1.0.0
pyaudio>=0.2.11
requests>=2.31.0
```

**Platform-specific audio dependencies:**

- **Windows**: `pip install pipwin && pipwin install pyaudio`
- **macOS**: `brew install portaudio && pip install pyaudio`
- **Linux**: `sudo apt-get install python3-pyaudio`

## 🎯 Usage

### Basic Voice Commands

**Ordering Items:**
```
"I want two burgers and fries"
"Give me one chocolate cake"
"Can I have three sodas?"
```

**Modifying Orders:**
```
"Remove the coca-cola"
"Cancel my burger"
"Delete the fries"
"Change my order - remove burger, add chicken"
```

**Getting Help:**
```
"What do you recommend?"
"What's popular?"
"Help me choose"
```

**Finishing Order:**
```
"I'm done"
"That's all"
"Checkout please"
```

### GUI Features

- **Menu Browser**: Click through categorized menu items
- **Order Management**: View, modify, and remove items
- **Voice Control**: Start/stop voice assistant
- **Real-time Status**: See system status and conversation log

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Speech Input  │ → │  Google Cloud   │ → │  Text Processing │
│   (Microphone)  │    │  Speech-to-Text │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Speech Output  │ ← │  Google Cloud   │ ← │   GPT-4 NLU     │
│   (Speakers)    │    │  Text-to-Speech │    │  Understanding  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Order System  │ ← │     Tkinter     │ ← │ Order Processing│
│    (JSON)       │    │      GUI        │    │   & Validation  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
voice-restaurant-system/
├── whisper_voice_bot.py      # Main application
├── config_template.py        # Configuration template
├── config.py                 # Your API keys (gitignored)
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
├── README.md                # This file
├── orders/                  # Order history (auto-created)
│   ├── order_20241201_143022.json
│   └── ...
└── temp_*.mp3              # Temporary audio files
```

## 🔒 Security

- **API keys are stored in `config.py`** (gitignored)
- **No hardcoded credentials** in source code
- **Service account JSON** files are gitignored
- **Temporary files** are cleaned up automatically

## 🛠️ Troubleshooting

### Common Issues

**1. "config.py not found"**
```bash
cp config_template.py config.py
# Edit config.py with your API keys
```

**2. "No audio input device"**
```bash
# Test microphone
python -c "import pyaudio; print('Audio devices:', pyaudio.PyAudio().get_device_count())"
```

**3. "Google Cloud authentication failed"**
- Verify service account JSON path
- Check API permissions in Google Cloud Console
- Ensure APIs are enabled

**4. "OpenAI API error"**
- Verify API key is correct
- Check account has credits
- Try different model (gpt-3.5-turbo vs gpt-4)

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. **Open** Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/voice-restaurant-system.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

## 📈 Roadmap

- [ ] **Multi-language support** for international restaurants
- [ ] **Voice training** for custom wake words
- [ ] **Kitchen integration** with order printing
- [ ] **Payment processing** integration
- [ ] **Customer database** with order history
- [ ] **Analytics dashboard** for restaurant insights
- [ ] **Mobile app** companion
- [ ] **Cloud deployment** options

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Cloud** for Speech and Text-to-Speech APIs
- **OpenAI** for GPT natural language understanding
- **Python community** for excellent libraries
- **Contributors** who help improve this project

## 📞 Support

- **Email**: abdallahalhasan2@gmail.com

---

**Made with ❤️ for restaurants everywhere**