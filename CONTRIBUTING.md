# Contributing to Home Server Orchestrator

Thanks for your interest in contributing! This project is intentionally minimal, so contributions should respect that philosophy.

---

## Getting Started

1. **Fork** the repository and clone it locally.
2. Copy `.env` and set your values:
   ```bash
   # Set HOST_IP to your LAN IP (or leave as localhost for local dev)
   HOST_IP=localhost
   ```
3. Build and run:
   ```bash
   docker compose up -d --build
   ```
4. Open `http://localhost:8080` to verify everything works.

---

## Project Structure

| Directory      | Purpose                              | Tech                  |
|----------------|--------------------------------------|-----------------------|
| `controller/`  | REST API + Docker management         | Python / FastAPI      |
| `ui/`          | Static single-page dashboard         | Vanilla HTML/CSS/JS   |
| `apps/`        | Managed app stacks (one folder each) | Docker Compose        |

---

## How to Contribute

### Report a Bug

Open an issue with:
- Steps to reproduce
- Expected vs actual behavior
- OS and Docker version (`docker version`)

### Suggest a Feature

Open an issue describing:
- The problem it solves
- A minimal proposed solution
- Whether you'd be willing to implement it

### Submit a Pull Request

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/my-change
   ```
2. Make your changes — keep them **small and focused**.
3. Test locally with `docker compose up -d --build`.
4. Verify:
   - The UI loads and displays apps correctly.
   - Start/Stop buttons work.
   - No errors in controller logs: `docker logs homeserver-controller`.
5. Submit the PR with a clear description of what and why.

---

## Code Guidelines

### General
- Keep it minimal. Don't add dependencies unless absolutely necessary.
- No unnecessary abstractions — flat is better than nested.
- Every file should have a clear single responsibility.

### Controller (Python)
- Follow PEP 8.
- Use type hints on all function signatures.
- Keep business logic in `app_service.py`, Docker operations in `docker_manager.py`.
- Validate all user input (especially app slugs) before use.

### UI (HTML/CSS/JS)
- Everything stays in `index.html` — no build tools, no frameworks.
- Use CSS variables for theming.
- Vanilla JS only — no jQuery, no libraries (except `js-yaml` for config parsing).

### Managed Apps
- Must use **pre-built images** (no `build:` in compose files).
- Bind mounts should use `${HOST_APP_DIR}` for host-path resolution.
- Each app folder must contain: `docker-compose.yml`, `app.json`, and optionally `app.png`.

---

## Adding a New Example App

1. Create `apps/my-app/` with:
   - `app.json` — name, slug, description, port, github_url
   - `docker-compose.yml` — uses a published image, maps a port
   - `app.png` — square icon (optional)
2. Test it: start from the UI, verify the URL works, stop it.
3. Submit the PR.

---

## What We're Looking For

- Bug fixes
- UI/UX improvements (keeping it minimal)
- New example apps
- Documentation improvements
- Security hardening
- Test coverage

---

## What We'll Likely Decline

- Adding React, Vue, or any JS framework
- Adding a database
- Features that break the "single `docker compose up`" workflow
- Unnecessary abstraction layers

---

## Questions?

Open an issue — there are no dumb questions.
