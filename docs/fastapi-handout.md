# FastAPI & the Task API — Concepts + Exercises

**Where you are:** CLI → OOP/SRMS → SQL → the Python bridge (HTTP, async, pydantic, the SQLAlchemy ORM). Every piece you need for this is something you've already built once, separately.

**What this is:** a real web server — a **Task API** with signup, login, and tasks that belong to a user. fetch.py made you a *client*. This makes you a *server*. Your Repository context manager, your pydantic Student, your SQLAlchemy Book — they all come back here, just wired into HTTP instead of called directly.

**How to use this:** Read → Run → Do, same as before. Use the auto-generated docs at http://127.0.0.1:8000/docs constantly — it's a live, clickable form for every endpoint you write. Don't guess what a request looks like; open /docs and send one.

**Time:** about a week. Don't rush Part 4 (auth) — it's the one with the most ways to get subtly wrong.

## Setup (do this first)

mkdir task-api

cd task-api

py -m venv .venv

.\\venv\Scripts\Activate.ps1

pip install fastapi "uvicorn\[standard\]" sqlalchemy pydantic "python-jose\[cryptography\]" bcrypt python-multipart pytest httpx

pip freeze \| Out-File -Encoding utf8 requirements.txt

**Use** Out-File -Encoding utf8**, not** pip freeze \> requirements.txt**.** PowerShell's \> redirect defaults to UTF-16, which breaks pip install -r requirements.txt on anyone else's machine (mine included — this has now happened on three submissions, so it's going in the setup step itself this time).

Note we're installing bcrypt **directly**, not passlib. passlib's bcrypt backend is currently broken against recent bcrypt versions (I hit AttributeError: module 'bcrypt' has no attribute '\_\_about\_\_' testing this myself) — calling bcrypt directly is simpler anyway and sidesteps it entirely.

Make a .gitignore with .venv/, \_\_pycache\_\_/, \*.db. Commit per exercise, like before.

# PART 1 — Your First Endpoint

from fastapi import FastAPI

app = FastAPI()

@app.get("/")

def root():

return {"message": "hello"}

Run it: uvicorn main:app --reload. Open http://127.0.0.1:8000/docs — FastAPI builds that page from your code automatically.

**Path and query params** come straight from type hints:

@app.get("/tasks/{task_id}")

def get_task(task_id: int, verbose: bool = False):

\# task_id comes from the URL path: /tasks/5

\# verbose is an optional query param: /tasks/5?verbose=true

...

**A request body** is just a pydantic model as a parameter — this is the part that should feel familiar:

from pydantic import BaseModel

class TaskCreate(BaseModel):

title: str

@app.post("/tasks")

def create_task(task_in: TaskCreate):

\# FastAPI parses the JSON body, validates it against TaskCreate,

\# and hands you a real TaskCreate object. Bad data -\> automatic 422, no code from you.

return {"title": task_in.title}

That's the whole trick of FastAPI: @app.get(...) is a decorator (Part 0.4 of the bridge handout), the body is a pydantic model (Part 4), and the handler can be async def (Part 3) when it awaits something. Nothing new — just assembled.

### Exercise 1

In a fresh main.py: 1. A GET / that returns a welcome message. 2. A GET /tasks/{task_id} that returns {"task_id": task_id}. 3. A POST /tasks that accepts {"title": str} and echoes it back. 4. Open /docs and call all three from the browser before writing any more code.

# PART 2 — Dependency Injection (Depends)

**You already do this.** Your Repository context manager opens a resource, hands it to the code that needs it, and guarantees cleanup. Depends is FastAPI's version of exactly that idea, but for *request handlers* instead of a with block.

from sqlalchemy.orm import Session

from fastapi import Depends

def get_db():

"""Yield a session, and always close it — same job your Repository does."""

with Session(engine) as session:

yield session

@app.get("/tasks")

def list_tasks(db: Session = Depends(get_db)):

\# FastAPI calls get_db() for you, hands you the session, closes it after.

return db.scalars(select(Task)).all()

yield instead of return is what makes the cleanup work — code after yield (none here, since the with block handles it) would run after the request finishes. You'll see the same yield shape again for auth in Part 4.

### Exercise 2

Set up database.py with a Base, an engine (sqlite:///tasks.db), and a get_db() dependency. You'll use it in every route from here on.

# PART 3 — Two Models, Not One

A real app keeps the **database table** and the **API shape** as two separate classes, even when they look similar:

\# models.py -- the SQLAlchemy table (how it's stored)

from sqlalchemy import ForeignKey, String

from sqlalchemy.orm import Mapped, mapped_column

from database import Base

class User(Base):

\_\_tablename\_\_ = "users"

id: Mapped\[int\] = mapped_column(primary_key=True)

username: Mapped\[str\] = mapped_column(String(50), unique=True)

password_hash: Mapped\[str\] = mapped_column(String(100))

class Task(Base):

\_\_tablename\_\_ = "tasks"

id: Mapped\[int\] = mapped_column(primary_key=True)

title: Mapped\[str\] = mapped_column(String(200))

done: Mapped\[bool\] = mapped_column(default=False)

owner_id: Mapped\[int\] = mapped_column(ForeignKey("users.id"))

\# schemas.py -- the pydantic shape (what the API sends/receives)

from pydantic import BaseModel, field_validator

class TaskCreate(BaseModel):

title: str

@field_validator("title")

@classmethod

def title_not_blank(cls, value: str) -\> str:

if not value.strip():

raise ValueError("title cannot be blank")

return value

class TaskOut(BaseModel):

id: int

title: str

done: bool

model_config = {"from_attributes": True} \# lets TaskOut read straight off a Task row

Why bother with two? The table shouldn't need to know about validation messages, and the API shouldn't expose password_hash just because User has one. They change for different reasons — so they're different classes.

### Exercise 3

1.  Define User and Task tables in models.py (ForeignKey from Task.owner_id to User.id — same relationship shape as your library.py Book, just pointing at a person instead of nothing).

2.  Define TaskCreate (validated, non-blank title) and TaskOut (from_attributes) in schemas.py.

3.  Base.metadata.create_all(engine) once, at startup, in main.py.

# PART 4 — Auth: Hashing, Login, JWT

**Never store a plain password.** Hash it with bcrypt — a hash you *cannot* reverse, built to be slow on purpose so guessing is expensive:

import bcrypt

def hash_password(password: str) -\> str:

return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, password_hash: str) -\> bool:

return bcrypt.checkpw(password.encode(), password_hash.encode())

**A JWT (JSON Web Token)** is how the server remembers you're logged in, without a server-side session. It's a signed string — anyone can *read* what's inside it (it's not encrypted), but only the server can *produce a valid one*, because only the server has SECRET_KEY:

from datetime import datetime, timedelta, timezone

from jose import jwt

SECRET_KEY = "dev-secret-change-in-real-life"

ALGORITHM = "HS256"

def create_access_token(username: str) -\> str:

expire = datetime.now(timezone.utc) + timedelta(minutes=30)

payload = {"sub": username, "exp": expire} \# exp = when this token stops working

return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

exp **is not optional.** A token with no expiry is a password that never needs changing — if it ever leaks, it works forever. Set it, and prove it works by building an already-expired token and confirming the server rejects it (the exercise asks for exactly this).

**Reading the token back**, as a dependency — this is the one that protects your routes:

from fastapi import Depends, HTTPException, status

from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -\> User:

error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

try:

payload = jwt.decode(token, SECRET_KEY, algorithms=\[ALGORITHM\])

username = payload.get("sub")

if username is None:

raise error

except JWTError:

raise error

user = db.scalars(select(User).where(User.username == username)).first()

if user is None:

raise error

return user

Any route that adds current_user: User = Depends(get_current_user) is now protected — FastAPI runs this dependency before your route body, and it either hands you a real User or the request never reaches your code.

### Exercise 4

1.  POST /signup — take a username + password (pydantic-validated: password at least 8 characters), reject a username that's already taken (400), store the hash, never the raw password.

2.  POST /login — take OAuth2PasswordRequestForm = Depends() (gives you .username/.password from form data, not JSON — that's what the login form in /docs expects), verify the password, return {"access_token": ..., "token_type": "bearer"}.

3.  get_current_user as a dependency, used by at least one route.

4.  Prove the expiry works: build a token with exp already in the past and confirm a protected route rejects it with 401.

# PART 5 — Ownership, and a Deliberate Contrast

Not every endpoint needs the same protection, and seeing both side by side is the point:

@app.get("/tasks")

def list_all_tasks(db: Session = Depends(get_db)):

"""Public on purpose: anyone can browse what tasks exist, no login required."""

return db.scalars(select(Task)).all()

@app.get("/tasks/mine")

def list_my_tasks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

"""Protected AND filtered: only this user's own tasks."""

return db.scalars(select(Task).where(Task.owner_id == current_user.id)).all()

get_current_user as a dependency makes a route *protected*. Filtering the query by current_user.id makes it *ownership-scoped*. Those are two separate decisions — a route can be protected but show everyone's data (rare, usually a mistake), or it can filter by owner. Know which one you're writing for each route.

### Exercise 5

1.  GET /tasks — public, returns every task from every user. (Yes, really — this is the deliberate contrast, not an oversight.)

2.  GET /tasks/mine — protected, only the current user's tasks.

3.  POST /tasks — protected, the new task's owner_id is the current user, not something the client gets to pick.

4.  DELETE /tasks/{task_id} — protected, **and ownership-checked**: if the task belongs to someone else, return 403, not 204. Test this with two different users.

# PART 6 — Tests

A route you've only clicked through in /docs is a route you haven't actually checked. TestClient sends real requests to your app without a running server:

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_create_task_requires_auth():

r = client.post("/tasks", json={"title": "no auth"})

assert r.status_code == 401

### Exercise 6

In test_main.py, write at least: 1. Signing up the same username twice fails. 2. Logging in with the wrong password fails. 3. Creating a task with no token fails (401). 4. Two different users each only see their own tasks via /tasks/mine. 5. A user cannot delete another user's task (403).

Run with pytest. All should pass.

## MINI CAPSTONE — the whole Task API

Put Parts 1–6 together into one app: signup → login → create tasks → list your own → list everyone's (public) → delete your own → can't delete someone else's. Then write the written answers below based on *your own* running code, the same way you did for the bridge capstone.

## What "done well" looks like

| Area                 | Full marks                                                                                                                  |
|------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| Routes               | Path/query params and a pydantic request body all work; /docs is usable                                                     |
| Dependency injection | get_db used everywhere a session is needed; no bare Session() calls in route bodies                                         |
| Models vs schemas    | Table and API shape kept separate; TaskOut never leaks password_hash                                                        |
| Auth                 | Passwords hashed, never stored raw; JWT has a real exp, and an expired token is proven to fail                              |
| Ownership            | /tasks (public) and /tasks/mine (protected+filtered) both exist and behave differently on purpose |
| Tests                | All 5 cases in Exercise 6 pass                                                                                              |

## Review questions (come ready to answer)

- Why do we hash passwords instead of storing them as plain text — and why bcrypt instead of a plain hash like SHA-256?

- A JWT isn't encrypted — anyone can decode and read what's inside it. So what actually stops someone from forging one?

- Why is /tasks public but /tasks/mine protected? What's the teaching point of having both in the same API?

- What would happen if you removed the exp claim from the JWT payload entirely?

- Walk me through what happens when one user tries to delete another user's task — which check stops it, and where in the code does it live?

## After this

Next stop is **Docker** — you'll containerize this exact API: a real Postgres instead of SQLite, a non-root user in the image, and a multi-stage build. Same API, just made to actually run somewhere that isn't your laptop.
