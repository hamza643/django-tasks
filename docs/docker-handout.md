# Docker — Packaging & Running Your API Anywhere

**Where you are:** you've built a working FastAPI Task API — routes, database, auth, tests. Right now it runs one way: on your machine, in your venv, with your exact Python version. Docker is how you package it so it runs **identically anywhere** — your machine, a teammate's, a server on the other side of the world.

**How to use this:** **Read → Run → Do.** Every command in this handout was tested against a real FastAPI + Postgres setup before being written down — run them yourself and watch what happens.

# PART 0 — What is Docker, and why does it exist?

## The problem it solves

"It works on my machine" is the most infamous sentence in software. Your FastAPI app runs fine for you — Python 3.12, these exact package versions, this OS. Your teammate has Python 3.10 and a different SQLAlchemy version. It breaks for them. A production server has yet another setup. It breaks there too, differently.

**Docker packages your application together with everything it needs to run** — the Python interpreter, every dependency, the OS-level libraries underneath — into one unit called an **image**. Anyone who runs that image gets the exact same environment you built and tested. Not "should work the same" — *is* the same, bit for bit.

## Container vs. virtual machine (the distinction that makes it click)

A **virtual machine** boots a whole separate operating system inside yours — its own kernel, its own everything. Heavy, slow to start (minutes), and each one uses gigabytes of disk.

A **container** shares your machine's OS kernel and only packages the application layer on top. It starts in **milliseconds to a couple of seconds**, and images are typically megabytes, not gigabytes. Containers aren't "lightweight VMs" — they're a fundamentally different mechanism (OS-level process isolation, not hardware virtualization) that happens to achieve similar isolation goals far more cheaply.

## Image vs. container — the one distinction you'll use constantly

- An **image** is the packaged blueprint — your app + dependencies + OS libraries, frozen as a file. You build it once.

- A **container** is a *running instance* of an image — like a class vs. an object, if you want the OOP parallel. You can run the same image as multiple containers at once.

docker build -t task-api . \# build the IMAGE (the blueprint)

docker run task-api \# start a CONTAINER (a running instance of it)

## Why you, specifically, need this

1.  **Deployment.** Real hosting platforms (AWS, Railway, Fly.io, your own server) run containers, not "a folder with a venv." This is how your FastAPI project actually goes live.

2.  **Team consistency.** No more "works on my machine" — everyone runs the identical environment.

3.  **It's how AI applications ship.** Model libraries (torch, transformers) are large and version-sensitive. Every real AI service you'll build from here on is containerized — this is the on-ramp to that phase, not a detour from it.

## Benefits

- **Consistency** — dev, staging, and production run the identical environment.

- **Isolation** — your app's dependencies can't collide with anything else on the host, or with another container's dependencies.

- **Portability** — the same image runs on your laptop, a teammate's machine, or any cloud provider that supports containers (essentially all of them).

- **Fast startup, small footprint** — compared to a VM, by orders of magnitude.

- **Reproducibility** — a Dockerfile is a recipe; anyone can rebuild the exact same image from it, and it can be version-controlled like code.

## Drawbacks — be honest about these too

- **A real learning curve.** Dockerfiles, compose files, networking between containers, volumes — it's a genuine new skill, not a checkbox.

- **Resource overhead exists,** even if it's much lighter than a VM. Running several containers on a small laptop can be noticeably heavier than running processes natively.

- **Debugging is one layer removed.** When something breaks *inside* a container, you can't just attach your usual debugger the way you would on your host — you need container-specific techniques (docker logs, docker exec).

- **Persistent data needs deliberate handling.** A container's filesystem is disposable by default — stop and remove it, and anything written inside is gone unless you explicitly used a volume. This trips up beginners with databases specifically.

- **Windows/Mac overhead.** Docker Desktop runs a lightweight VM under the hood on non-Linux hosts, because containers need a Linux kernel. It works well, but it's not "zero overhead" outside Linux.

The honest summary: Docker adds a layer of things to learn and manage, in exchange for solving a much bigger, much more common problem (environment inconsistency). For anything beyond a personal script, that trade is almost always worth it — which is why it's now close to universal in the industry.

### Do it

Run docker --version and docker compose version. If either fails, install Docker Desktop (Windows/Mac) or Docker Engine (Linux) before continuing.

# PART 1 — Your first Dockerfile

A Dockerfile is a text file of instructions for building an image, read top to bottom.

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD \["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"\]

- FROM python:3.12-slim — start from an existing image with Python already installed. slim is a smaller variant than the default (fewer preinstalled OS packages) — smaller images pull and start faster, and have a smaller attack surface.

- WORKDIR /app — every instruction after this runs inside /app in the image.

- COPY requirements.txt . then RUN pip install ... — copy *only* the dependency list first, install it, and *then* copy the rest of the code. This order is deliberate — see layer caching below.

- COPY . . — copy the rest of your project in.

- EXPOSE 8000 — documents which port the app listens on (informational; doesn't actually publish it — that happens with -p at run time).

- CMD \[...\] — the command that runs when a container starts.

Build and run it:

docker build -t task-api . \# -t names the image "task-api"

docker run -p 8000:8000 task-api \# -p host_port:container_port

Open http://localhost:8000/health — you're now talking to your app running inside a container.

### CMD vs RUN

- RUN executes **during the build** and its result is baked into the image (e.g. installing packages).

- CMD is the command that runs **when a container starts**, and there's only one per Dockerfile (the last one wins if you write several).

### Do it

Containerize a minimal FastAPI app (just a /health endpoint is enough to start) using the Dockerfile above. Confirm docker run + a curl to /health works.

# PART 2 — Layer caching (why build order matters)

Docker builds an image as a stack of **layers**, one per instruction, and caches each one. On a rebuild, it reuses every layer up to the first one that actually changed.

This is *why* COPY requirements.txt . + RUN pip install happens **before** COPY . .:

- Change a line in main.py → the requirements.txt copy and the pip install layers are **unchanged**, so Docker reuses them instantly and only re-does the final COPY.

- If you'd written COPY . . first, changing *any* file — even a comment — would invalidate everything after it, including the expensive pip install, and every rebuild would reinstall every dependency from scratch.

### Do it

Build your image once. Then change one line in main.py (not requirements.txt) and rebuild. Watch the output — the pip install step should say CACHED, and the rebuild should be near-instant. Then change something in requirements.txt and rebuild — now the install step actually re-runs.

# PART 3 — .dockerignore

Without one, COPY . . copies **everything** in your project folder into the image — your .venv/, .git/, \_\_pycache\_\_/, and worst of all, your .env file with real secrets in it.

Create .dockerignore (same syntax as .gitignore):

.venv/

\_\_pycache\_\_/

\*.pyc

.git/

.env

\*.db

This matters for three reasons: smaller, faster builds; a smaller image; and — the one that actually matters most — **secrets never end up baked into an image that might get pushed to a registry** other people can pull.

### Do it

Add a .dockerignore to your project. Rebuild and confirm the build context size shrinks (Docker prints how many bytes it "sent" during the build).

# PART 4 — Multi-stage builds & running as a non-root user

Two production-grade improvements over Part 1's Dockerfile.

\# --- Stage 1: build ---

FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

\# --- Stage 2: runtime ---

FROM python:3.12-slim

RUN useradd --create-home appuser

WORKDIR /app

COPY --from=builder /root/.local /home/appuser/.local

COPY . .

RUN chown -R appuser:appuser /app

USER appuser

ENV PATH=/home/appuser/.local/bin:\$PATH

EXPOSE 8000

CMD \["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"\]

**Multi-stage builds** — the first stage installs dependencies (which needs build tools you don't want in your final image); the second stage copies over *only the installed packages*, not the build tools. COPY --from=builder reaches into the first stage and pulls just what's needed. The result: a smaller final image with less attached baggage.

**Non-root user** — by default a container runs as root. If an attacker ever finds a way to execute code inside your container, running as root hands them far more power than they need. useradd + USER appuser means the app runs with an ordinary, unprivileged user instead — a real security practice, not a formality.

### Do it

Rewrite your Dockerfile using this multi-stage pattern. Confirm the app still runs, then run docker exec \<container\> whoami — it should print appuser, not root.

# PART 5 — docker-compose: multiple containers together

Your API needs a database too. **docker-compose** defines multiple containers (called "services") and how they connect, in one YAML file.

services:

db:

image: postgres:16-alpine

environment:

POSTGRES_USER: taskapi

POSTGRES_PASSWORD: devpassword

POSTGRES_DB: tasks

healthcheck:

test: \["CMD-SHELL", "pg_isready -U taskapi"\]

interval: 3s

timeout: 3s

retries: 5

api:

build: .

ports:

- "8000:8000"

environment:

DATABASE_URL: postgresql://taskapi:devpassword@db:5432/tasks

depends_on:

db:

condition: service_healthy

Run the whole stack with one command:

docker compose up -d --build \# -d = detached (runs in the background)

docker compose down \# stop and remove everything

Three things worth understanding:

- **Services can reach each other by name.** Your api container connects to db:5432 — db is not an IP address, it's the service name, resolved automatically over an internal Docker network compose creates for you.

- depends_on **with** condition: service_healthy makes api wait until the healthcheck reports Postgres is actually ready to accept connections — not just "the container started," which is a common source of confusing startup failures (the app crashes because it tried to connect a half-second before the database was ready).

- **This is the moment you swap SQLite for real Postgres — and your application code barely changes.** If your database connection reads its URL from an environment variable (os.environ\["DATABASE_URL"\]), the entire migration from SQLite to Postgres is the string above. This is exactly the payoff of using an ORM: your models, your queries, your routes — none of it changes.

### Do it

Add a db service to a docker-compose.yml for your Task API, point DATABASE_URL at it, and confirm docker compose up brings up both containers with the API successfully talking to Postgres instead of SQLite.

# PART 6 — Security & logging (a short, important detour)

Two habits that matter the moment your code runs somewhere other than your own laptop.

## Never commit secrets

You've now built .env files, JWT secret keys, and database passwords. **None of these ever belong in a Dockerfile, a docker-compose file committed to Git, or your image.** Pass them at *runtime* instead:

docker run --env-file .env task-api

\# docker-compose.yml

api:

env_file: .env

The .env file itself stays in .gitignore and .dockerignore — never committed, never baked into an image.

**Why this isn't hypothetical:** this exact company had a real incident where credentials were exposed in a public JavaScript bundle for years because a secret was marked with a public-facing prefix (NEXT_PUBLIC\_...) instead of being kept server-side. The fix, once discovered, was to move the credential behind a server-only environment variable — precisely the env_file pattern above. The lesson: a secret baked into anything that ships to users or into a public image is a secret that's already leaked, whether anyone's noticed yet or not.

## Use logging, not print

print() output is easy to lose once your app runs in a container on a remote server — you're not sitting at a terminal watching it. Python's logging module gives you levels, timestamps, and output you can actually collect and search later:

import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(\_\_name\_\_)

logger.info("Task %s created by user %s", task.id, user.email)

logger.warning("Login failed for %s", email)

logger.error("Database connection failed: %s", exc)

Container logs are viewed with:

docker logs \<container_name\>

docker logs -f \<container_name\> \# -f follows, like tail -f

### Do it

Replace any print() statements in your Task API with logging calls at the appropriate level (info for normal events, warning for recoverable problems, error for failures). Confirm docker logs shows them.

# THE ASSIGNMENT — Containerize the Task API

Take your FastAPI Task API (from the previous assignment) and ship it properly.

**Requirements:** 1. A **multi-stage Dockerfile** — small final image, runs as a **non-root user**. 2. A .dockerignore that excludes .venv/, \_\_pycache\_\_/, .git/, .env, and any .db files. 3. A docker-compose.yml bringing up your API **and a Postgres container** — no more SQLite. Use a healthcheck + depends_on so the API doesn't start before the database is ready. 4. **No secrets in any committed file.** Your JWT secret and database credentials come from a .env file, loaded via env_file:, and .env is gitignored. 5. Replace remaining print() calls with logging. 6. Confirm your existing test suite still passes when run against the containerized Postgres setup (you may need a DATABASE_URL pointing at a test database). 7. **A** README.md **update**: how to build and run the whole stack with docker compose up, and how someone else could clone your repo and have it running with one command.

**Stretch goals:** - Add a healthcheck to the api service itself (hit /health). - Get the final image under 200MB — report the size before and after your multi-stage rewrite. - A compose.override.yml for local dev (hot-reload) vs. a leaner production config.

## What "done well" looks like

| Area          | Full marks                                                           |
|-----------------------------------------|------------------------------------------------------------------------------------------------|
| Dockerfile    | Multi-stage, non-root user, sensible layer ordering                  |
| .dockerignore | No secrets or bloat land in the build context                        |
| Compose stack | API + Postgres both come up; depends_on + healthcheck used correctly |
| Secrets       | Nothing sensitive committed anywhere; .env + env_file used correctly |
| Logging       | logging module used with sensible levels, not print                  |
| Documentation | docker compose up genuinely works from a clean clone, first try      |

## Review questions

- "What's the difference between an image and a container — in your own words?"

- "Why does your Dockerfile copy requirements.txt before the rest of the code? What happens if you reverse that order?"

- "Your db service and api service talk to each other — how does api find db? Is it an IP address?"

- "Where does your JWT secret live now, and why isn't it in the Dockerfile?"

- "What's one real drawback of Docker you ran into yourself while doing this?"
