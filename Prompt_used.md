You are a senior platform engineer and system architect.

I want you to design and generate a complete minimal but production-quality implementation of a self-hosted Docker Home Server Orchestrator.

You must reason step by step about architecture decisions before generating code.

Requirements:

SYSTEM OVERVIEW:
- Everything must run inside Docker.
- A single root docker-compose.yml must launch the whole system.
- The system manages independent apps stored in /apps.
- Each app has:
    - docker-compose.yml
    - app.json (metadata)
    - app.png

ARCHITECTURE:
- UI (frontend)
- App Controller (FastAPI backend)
- Apps folder with independent docker-compose stacks

FUNCTIONAL REQUIREMENTS:
1. UI must display:
   - App image
   - App name
   - Description (as dropdown)
   - GitHub link (as dropdown)
   - Public URL (for now it will be localhost:port)
   - Status (running / stopped)(by calling to health of the application)
   - Launch button
   - Stop button

2. Controller must:
   - Dynamically read /apps folder
   - Parse each app.json
   - Execute docker compose up -d inside the selected app folder if the user click on launch button
   - Execute docker compose down if the user clicks on stop button
   - Detect running status using Docker API or docker CLI
   - Expose REST API:
        GET /apps
        POST /apps/{app}/start
        POST /apps/{app}/stop

3. Everything must be:
   - Clean
   - Minimal
   - Secure enough for a home server
   - Structured professionally
   - Well separated by responsibilities

4. Use:
   - FastAPI for backend
   - Docker CLI inside controller container
   - React + Vite (minimal UI)
   - Multi-stage Docker builds where appropriate

5. Create a simple example with an app to be a nginx, so i can see that everything works and i can test the functionalities

DELIVERABLES:
- Full folder structure
- Full docker-compose.yml (root)
- Controller code (complete)
- UI code (minimal but working)
- Example app inside /apps
- Dockerfiles for everything
- Explanation of design decisions

Be minimal but production-minded.
Avoid unnecessary abstractions.
Focus on clarity, robustness, and clean structure.

structure of the repo: 
homeserver-orchestrator/
│
├── docker-compose.yml
├── .env
│
├── controller/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── routes.py
│       ├── docker_manager.py
│       ├── app_service.py
│       ├── models.py
│       └── config.py
│
├── ui/
    ├── Dockerfile
    ├── config
    │   ├── assets
    │   │   ├── UI-logo.png
    │   └── config.yaml
    └── index.html
│
└── apps/
    │
    └── example-nginx/
        ├── docker-compose.yml
        ├── app.json
        └── app.png

if you have any further questions, ask me before starting everything

Your folder structure shows a plain `index.html` with `config.yaml`, but requirements say 'React + Vite'. Which approach do you want?
Plain HTML/CSS/JS (single index.html, no build step)
- Simpler, served by nginx, no node_modules. Config via config.yaml or JS.
What host ports should the UI and controller API bind to?
UI: 8080 and API 8081
For 'Description as dropdown' and 'GitHub link as dropdown' — do you mean collapsible/expandable sections on each app card that reveal the text on click?
Yes, collapsible accordion sections
What is the `config/config.yaml` in the UI for? I'd suggest using it to hold the UI title, logo path, and API base URL so the UI is configurable without rebuilds.
Yes, use it for UI title + logo + API URL