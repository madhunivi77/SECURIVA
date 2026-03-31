# SECURIVA
The project focuses on developing an AI-assisted platform that automates and manages key business operations while maintaining strong cybersecurity safeguards.

## Features

### Voice AI Assistant (VAPI Integration)
SECURIVA includes a voice-enabled AI assistant powered by [VAPI](https://vapi.ai). Users can interact with the platform using natural speech.

**Capabilities:**
- Voice-to-text transcription (Deepgram Nova-2)
- AI-powered responses (GPT-4o-mini via custom LLM endpoint)
- Text-to-speech output (Deepgram Asteria voice)
- Real-time conversation with visual feedback (3D animated orb)

**Architecture:**
```
User speaks → VAPI (Deepgram STT) → Custom LLM Endpoint → OpenAI/LangGraph
                                                              ↓
User hears  ← VAPI (Deepgram TTS) ← Response ←───────────────┘
```

### MCP Tools Integration
When authenticated, the voice assistant has access to:
- **Gmail**: List emails, read content, create drafts, summarize
- **Google Calendar**: List events, create events, manage attendees
- **Salesforce**: Create/list contacts, accounts, opportunities, cases; SOQL/SOSL search; send emails; Chatter posts; tasks/events; file management (26 tools)
- **TeleSign**: Send SMS/voice calls, phone verification, 2FA codes, fraud risk assessment, message status tracking, batch operations (13 tools)

### 3D Voice Interface
- Animated WebGL orb using Three.js and React Three Fiber
- Color-coded states (gray=idle, purple=active, green=listening, indigo=speaking)
- Real-time audio-reactive animations

---




# Contributing Guidelines    
Following are the guidelines to ensure smooth collaboration and integration. 

---

## Branching Model
We follow a **GitHub Flow** style branching model:  

- **`main`** → Production-ready, stable code.  
- **`dev`** → Integration/testing branch.  
- **`feature/*`** → One branch per feature (e.g., `feature/login-auth`, `feature/api-integration`).  

**Rules:**  
- Do **not** commit directly to `main` or `dev`.  
- Always branch off from `dev`.  
- Create a Pull Request (PR) when a feature is ready.  

## Commit Message Conventions (Taiga Integration)
To keep GitHub and Taiga linked, reference Taiga task IDs in your commit messages:  

- `TG-123` ->Links commit to task/story **123**.  
- `TG-123` -> Closes task/story **123**.  
- `TG-123 ready for test` -> Moves task **123** to *Ready for Test*.  

**Examples:**  
```bash
git commit -m "Add login API TG-45"
git commit -m "Fix authentication bug TG-46"
git commit -m "Update test cases for signup TG-47"
```

## Local Testing

Local testing may be conducted 1 of 2 ways: 

### Command Line
Frontend:<br>
- Ensure that node packages are installed with `npm install`<br>
- Ensure that voice agent environment variables are set in .env<br>
- Run `npm run dev` and navigate to the corresponding vite link

Backend:<br>
- Ensure that environment variables are set in .env<br>
- run `uv sync` to install packages from uv.lock<br>
- Run `uv run run.py`

### Docker
With docker installed (For ease use we recommend Docker Desktop):
- You MUST set /backend/run.py host address to 0.0.0.0 for correct mapping
- Ensure that Docker is properly recognized in your command line environment using the following commands:<br>
```
docker --version
docker compose version
docker ps
```
- Simply run `docker compose up --build`. This will create a docker network as well as a frontend and backend container
- When finished, `docker compose down`
- To clean up after rebuilds, use `docker system prune`