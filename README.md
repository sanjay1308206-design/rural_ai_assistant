🌾 Rural AI Assistant
AI-powered assistant for Indian farmers — fully local, free, and multilingual
________________________________________
🚀 Overview
Rural AI Assistant is a production-ready AI system designed to help farmers with:
•	🌾 Crop guidance 
•	🪱 Soil & fertilizer advice 
•	🐛 Pest & disease solutions 
•	🌦️ Weather-based recommendations 
•	📋 Government schemes 
It runs 100% locally using Ollama (llama3) — no API key, no cloud dependency, no cost.
________________________________________
✨ Key Features
🧠 Intelligent Q&A (RAG-based)
•	Uses FAISS vector database 
•	Retrieves relevant agricultural knowledge 
•	Generates contextual answers using llama3 
🌐 Multilingual Support
•	Supports Indian languages: 
o	English, Hindi, Tamil, Telugu, Kannada, Bengali, Marathi, etc. 
•	Auto translation using deep-translator 
🎤 Voice Assistant
•	Speech-to-text using Whisper (offline) 
•	Text-to-speech using gTTS 
•	Full voice interaction capability 
🌦️ Weather Integration
•	Real-time weather data (OpenWeather API) 
•	Smart farming advisories 
⚡ Fully Offline AI
•	Runs locally via Ollama 
•	No API cost, no internet dependency for LLM 
________________________________________
🏗️ Tech Stack
Backend
•	FastAPI 
•	FAISS (Vector Search) 
•	Sentence Transformers (Embeddings) 
•	Ollama (llama3 LLM) 
•	Whisper (Speech-to-Text) 
Frontend
•	Streamlit (Modern UI) 
Utilities
•	deep-translator (Multilingual support) 
•	gTTS (Text-to-Speech) 
________________________________________
📁 Project Structure
app/
 ├── routes/
 │    ├── query.py
 │    └── voice.py
 ├── services/
 │    ├── rag_pipeline.py
 │    ├── retriever.py
 │    ├── llm.py
 │    ├── weather_service.py
 │    ├── speech_to_text.py
 │    └── text_to_speech.py
 ├── utils/
 │    ├── intent.py
 │    ├── translator.py
 │    └── chunking.py
 ├── config.py
 └── main.py

frontend/
 └── app.py

scripts/
 └── ingest_data.py

data/
 └── raw/
________________________________________
⚙️ Setup Instructions
1. Install Ollama
Download and install:
https://ollama.com/download
________________________________________
2. Pull llama3 Model
ollama run llama3
________________________________________
3. Create .env File
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434
LLM_MAX_TOKENS=512
LLM_TEMPERATURE=0.3
WHISPER_MODEL=base
TOP_K_RESULTS=4
________________________________________
4. Install Dependencies
pip install -r requirements.txt
________________________________________
5. Build Vector Database
python scripts/ingest_data.py
________________________________________
6. Run Backend
uvicorn app.main:app --reload --port 8000
________________________________________
7. Run Frontend
streamlit run frontend/app.py
________________________________________
📡 API Endpoints
Endpoint	Method	Description
/api/ask	POST	Main AI Q&A
/api/health	GET	System health
/api/validate-key	GET	Ollama check
/api/voice/transcribe	POST	Speech → Text
________________________________________
🧠 How It Works
1.	User query → Intent detection 
2.	Query translated to English 
3.	FAISS retrieves relevant chunks 
4.	Context + query → llama3 
5.	Answer generated 
6.	Translated back to user language 
7.	Optional voice output 
________________________________________
🎯 Use Cases
•	Farmers needing crop advice 
•	Rural education systems 
•	Agriculture extension tools 
•	Offline AI assistants for villages 
________________________________________
🔥 Highlights
•	✅ Fully offline AI system 
•	✅ No API cost 
•	✅ Multilingual + Voice enabled 
•	✅ Production-ready FastAPI backend 
•	✅ Scalable RAG architecture 
________________________________________
⚠️ Known Limitations
•	First-time model load may take ~30 seconds 
•	Accuracy depends on dataset quality 
•	Weather requires API key for real data 
________________________________________
📈 Future Improvements
•	Mobile app integration 
•	IoT sensor data integration 
•	Advanced crop prediction models 
•	Regional dataset expansion 
________________________________________
🤝 Contributing
Pull requests are welcome. For major changes, open an issue first.
________________________________________
📜 License
MIT License
________________________________________
👨‍💻 Author
Sanjay kumar M 
AI/ML Developer

