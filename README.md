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

## Architecture & System Design

```
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                          SECURIVA — SYSTEM ARCHITECTURE                             ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND  (React + Vite · :5173)                       │
│                                                                                     │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  Auth Pages   │  │  Agent Pages  │  │  Dashboard/Logs  │  │  Landing / Info  │  │
│  │  Login/Signup │  │  AgentText    │  │  Dashboard.jsx   │  │  Homepage.jsx    │  │
│  │  Google OAuth │  │  AgentVoice   │  │  Logs.jsx        │  │  Features.jsx    │  │
│  │  ProviderForm │  │  VapiWidget   │  │  ChatSidebar     │  │  Pricing.jsx     │  │
│  └───────┬───────┘  └──────┬────────┘  └────────┬─────────┘  └──────────────────┘  │
│          │                 │                    │                                   │
│          └─────────────────┴────────────────────┘                                  │
│                             ProtectedRoute (JWT check)                              │
└──────────────────────────────────────┬──────────────────────────────────────────────┘
                                       │  HTTPS / REST + SSE
┌──────────────────────────────────────▼──────────────────────────────────────────────┐
│                         BACKEND  (Starlette · Python 3.12 · :8000)                  │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │  AUTH LAYER                                                                 │    │
│  │  /login → Google OAuth2 Flow      /callback → JWT cookie + CSRF token      │    │
│  │  /api/voice-token  (GET)          /api/voice-session (POST) → voice JWT    │    │
│  │  /api/logout                      token_verifier.py  ·  bcrypt + pyjwt     │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                     │
│  ┌───────────────────────┐   ┌──────────────────────────────────────────────────┐   │
│  │  CORE API ROUTES      │   │  MOUNTED SUB-APPLICATIONS                       │   │
│  │  /api/status          │   │  /salesforce  → salesforce_app.py               │   │
│  │  /api/chat     (POST) │   │  /stripe      → stripe_app.py                  │   │
│  │  /api/logs     (GET)  │   │  /chat        → db_app  (DynamoDB)              │   │
│  │  /api/whatsapp/       │   │  /security    → security_app                   │   │
│  │   send-sms    (POST)  │   │  /vapi        → vapi_app (see VAPI layer)       │   │
│  └───────────┬───────────┘   └──────────────────────────────────────────────────┘   │
│              │                                                                      │
│  ┌───────────▼───────────────────────────────────────────────────────────────────┐  │
│  │  CHAT / AGENT ENGINE   (chat_handler.py · grounded_chat_policy.py)           │  │
│  │  request_validator.py → tool_confirmation_handler.py → execute_chat_tools()  │  │
│  │  guidance_store.py · guidance_catalog.py → grounded policy enforcement       │  │
│  └───────────────────────────────────┬───────────────────────────────────────────┘  │
│                                      │                                              │
│  ┌───────────────────────────────────▼───────────────────────────────────────────┐  │
│  │  MCP TOOL LAYER   (mcp_server.py · mcp_pool.py · compliance_mcp_server.py)   │  │
│  │                                                                               │  │
│  │  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐  ┌─────────────────┐  │  │
│  │  │  Compliance  │  │  TeleSign     │  │  Salesforce  │  │  Security       │  │  │
│  │  │  compliance_ │  │  sendSMS()    │  │  CRM queries │  │  security_tools │  │  │
│  │  │  tools.py    │  │  verifyPhone()│  │  account ops │  │  encryption_svc │  │  │
│  │  │  PCI / SOX   │  │  sendWhatsApp │  │              │  │  api_key_mgr    │  │  │
│  │  │  generators  │  │  assessRisk() │  │              │  │                 │  │  │
│  │  └──────────────┘  └───────────────┘  └──────────────┘  └─────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │  VAPI VOICE LAYER   (vapi_webhook.py · voice_agent.py)                      │    │
│  │  /vapi/chat/completions → handle_custom_llm() → voice agent + MCP tools    │    │
│  │  /vapi/events          → handle_vapi_events() → call lifecycle hooks       │    │
│  │  Auth: voiceToken JWT extracted from call.assistant.metadata                │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │  OBSERVABILITY                                                              │    │
│  │  activity_logger.py · tool_logger.py · telesign_logging.py                 │    │
│  │  logs/tool_calls.log · logs/tool_calls.json · ai_calls.log (rotating)      │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────┬──────────────────────────────────────────────┘
                                       │
          ┌────────────────────────────┼─────────────────────────────┐
          │                            │                             │
          ▼                            ▼                             ▼
┌─────────────────┐          ┌─────────────────────┐      ┌──────────────────────┐
│  OPENAI (LLM)   │          │  EXTERNAL SERVICES  │      │  AWS / DATA LAYER    │
│  GPT-4o         │          │                     │      │                      │
│  Chat + Voice   │          │  ┌───────────────┐  │      │  DynamoDB            │
│  completions    │          │  │   TeleSign    │  │      │  TelesignLogs        │
│  Streaming SSE  │          │  │  SMS · OTP    │  │      │  GuidanceCatalog     │
└─────────────────┘          │  │  WhatsApp     │  │      │  ChatHistory         │
                             │  │  PhoneID      │  │      │  UserSessions        │
                             │  │  Score/Verify │  │      │                      │
                             │  └───────────────┘  │      │  credential_         │
                             │  ┌───────────────┐  │      │  integration.py      │
                             │  │  Salesforce   │  │      │  (DynamoDB-backed    │
                             │  │  CRM API      │  │      │   secret storage)    │
                             │  └───────────────┘  │      └──────────────────────┘
                             │  ┌───────────────┐  │
                             │  │    Stripe     │  │
                             │  │  Payments API │  │
                             │  └───────────────┘  │
                             │  ┌───────────────┐  │
                             │  │     VAPI      │  │
                             │  │  Voice AI     │  │
                             │  │  Orchestrator │  │
                             │  └───────────────┘  │
                             └─────────────────────┘

══════════════════════════════════════════════════════════════════════════════════════
  DATA FLOW — TEXT CHAT
  User → React ChatBox → POST /api/chat → request_validator → grounded_chat_policy
       → execute_chat_tools (OpenAI + MCP tools) → SSE stream → ChatBox render

  DATA FLOW — VOICE CALL
  User → VapiVoiceWidget → VAPI cloud → POST /vapi/chat/completions (voice JWT auth)
       → handle_custom_llm → voice_agent → MCP tools → streaming OpenAI response → VAPI TTS

  DATA FLOW — SMS / VERIFY
  MCP Tool call → telesign_auth.send_sms() / send_verification_code()
       → TeleSign API (sender_id=38788) → telesign_logging → DynamoDB TelesignLogs
══════════════════════════════════════════════════════════════════════════════════════
```

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