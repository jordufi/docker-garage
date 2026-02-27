# Home Server Orchestrator

A minimal, production-quality, self-hosted Docker home server dashboard.  
Manage independent Docker Compose stacks from a single UI.

---

## Quick Start

**1. Configure your network IP** (in `.env`):

```env
# Set this to your machine's LAN IP so app links work from other devices (e.g. phone).
# Find it with:  ipconfig  (Windows)  or  ip a  (Linux/macOS)
HOST_IP=192.168.1.50
```

If you only use the dashboard from the same machine, you can leave it as `localhost`.

**2. Launch the stack:**

```bash
docker compose up -d --build
```

**3. Open the dashboard:**

| From              | URL                              |
|-------------------|----------------------------------|
| Same machine      | http://localhost:8080             |
| Phone / other LAN | http://&lt;HOST_IP&gt;:8080      |

| Service    | URL                              |
|------------|----------------------------------|
| UI         | http://&lt;HOST_IP&gt;:8080      |
| API        | http://&lt;HOST_IP&gt;:8081      |
| API Docs   | http://&lt;HOST_IP&gt;:8081/docs |

---

## Architecture

```
┌──────────────────────────────────────────────────┐
│                  Host Machine                     │
│                                                   │
│   ┌──────────┐    ┌────────────┐                  │
│   │  UI      │───▶│ Controller │                  │
│   │ (nginx)  │    │ (FastAPI)  │                  │
│   │ :8080    │    │ :8081      │                  │
│   └──────────┘    └─────┬──────┘                  │
│                         │ docker.sock             │
│                         ▼                         │
│              ┌──────────────────┐                  │
│              │  Managed Apps    │                  │
│              │  /apps/*         │                  │
│              │  (independent    │                  │
│              │   compose stacks)│                  │
│              └──────────────────┘                  │
└──────────────────────────────────────────────────┘
```

**Key design decisions:**

- **Docker-out-of-Docker (DOOD)**: The controller mounts the host's Docker socket to manage app stacks. No Docker-in-Docker complexity.
- **Nginx reverse proxy**: The UI proxies `/api/*` to the controller, eliminating CORS issues and providing a single entry point.
- **Plain HTML/CSS/JS**: No build step, no node_modules. A single `index.html` with vanilla JavaScript.
- **Pre-built images only**: Managed apps must use published Docker images (no `build:` contexts) since DOOD cannot resolve container-internal paths for builds.
- **No authentication**: Designed for home LAN use. Add a reverse proxy with auth (e.g., Authelia, Traefik) for internet exposure.

---

## API Reference

| Method | Endpoint                     | Description              |
|--------|------------------------------|--------------------------|
| GET    | `/apps`                      | List all apps + status   |
| POST   | `/apps/{slug}/start`         | Start an app stack       |
| POST   | `/apps/{slug}/stop`          | Stop an app stack        |
| GET    | `/apps/{slug}/icon`          | Get app icon (PNG)       |
| GET    | `/health`                    | Controller health check  |

---

## Adding a New App

1. Create a folder under `apps/` (e.g., `apps/my-app/`)
2. Add three files:

**`app.json`** — metadata:
```json
{
    "name": "My App",
    "slug": "my-app",
    "description": "A short description of what this app does.",
    "github_url": "https://github.com/user/repo",
    "port": 8888
}
```

**`docker-compose.yml`** — the stack:
```yaml
version: "3.8"
services:
  myapp:
    image: some-image:latest
    ports:
      - "8888:80"
    restart: unless-stopped
```

**`app.png`** — a square icon (optional, a fallback is served if missing).

3. The app will appear in the UI on the next refresh (every 10 seconds by default).

---

## Folder Structure

```
homeserver/
├── docker-compose.yml          # Root orchestrator stack
├── .env                        # Port configuration
├── controller/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # FastAPI entry point
│       ├── routes.py           # REST API endpoints
│       ├── docker_manager.py   # Docker CLI wrapper
│       ├── app_service.py      # App discovery & metadata
│       ├── models.py           # Pydantic models
│       └── config.py           # Configuration
├── ui/
│   ├── Dockerfile
│   ├── nginx.conf              # Reverse proxy config
│   ├── index.html              # Single-page UI
│   └── config/
│       ├── config.yaml         # UI configuration
│       └── assets/
│           └── UI-logo.svg     # Dashboard logo
└── apps/
    └── example-nginx/          # Example managed app
        ├── docker-compose.yml
        ├── app.json
        └── app.png
```

---

## Configuration

### Environment Variables (`.env`)

| Variable          | Default     | Description                                          |
|-------------------|-------------|------------------------------------------------------|
| `HOST_IP`         | `localhost` | Your machine's LAN IP — used in app URLs             |
| `CONTROLLER_PORT` | `8081`      | Host port for the API                                |
| `UI_PORT`         | `8080`      | Host port for the UI                                 |
| `APPS_DIR`        | `./apps`    | Path to managed apps                                 |
| `HOST_APPS_DIR`   | auto-detect | Host-side absolute path to apps (for bind mounts)    |

### UI Configuration (`ui/config/config.yaml`)

| Key                | Default             | Description                    |
|--------------------|---------------------|--------------------------------|
| `title`            | `Home Server`       | Dashboard title                |
| `logo`             | `/config/assets/..` | Logo image path                |
| `api_url`          | `/api`              | API base URL                   |
| `refresh_interval` | `10`                | Auto-refresh interval (seconds)|

---

## Security Notes

- The Docker socket (`/var/run/docker.sock`) is mounted into the controller container. This grants effectively root-level access to the host. **Only run this on a trusted network.**
- App slugs are validated against `^[a-zA-Z0-9_-]+$` to prevent path traversal.
- For internet-facing deployments, place the system behind a reverse proxy with authentication (Authelia, Traefik, Caddy with basicauth, etc.).

---

## License

MIT