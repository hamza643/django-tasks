# Bridge to Backend & AI — Concepts + Exercises

**Where you are:** you've built a CLI app (functions, modules, JSON), an OOP project (classes, inheritance, context managers), and learned SQL. Strong base.

**What this bridges:** the handful of concepts that make web frameworks (FastAPI, Django) and AI engineering make *sense* instead of feeling like magic. Do this **before** touching a framework — skip it and you'll be copy-pasting code you don't understand.

**How to use this:** each section is **Read → Run → Do**. Don't just read the example — type it, run it, watch the output, then do the exercise. Reading Python and writing Python are different skills.

**Time:** about 3–5 days. Don't rush pydantic and async — they're the two that matter most.

## Setup (do this first)

mkdir bridge-practice

cd bridge-practice

py -m venv .venv \# Windows

.\\venv\Scripts\Activate.ps1 \# prompt should show (.venv)

pip install pydantic httpx sqlalchemy

pip freeze \> requirements.txt

Make a .gitignore with .venv/, \_\_pycache\_\_/, \*.db. Commit as you go, one commit per exercise.

# PART 0 — Python Essentials (consolidation)

Quick refresher on the Python a backend developer leans on daily. You've met some of these; make sure none are fuzzy.

## 0.1 Data structures — pick the right one

prices = \[10, 20, 30\] \# list: ordered, changeable

point = (4, 5) \# tuple: ordered, FIXED (can't change)

unique = {1, 2, 2, 3} \# set: no duplicates -\> {1, 2, 3}

student = {"name": "Ali", "age": 17} \# dict: key -\> value lookups

Rule of thumb: **list** for a sequence you'll change, **tuple** for a fixed pair/record, **set** for uniqueness, **dict** for lookups by key.

## 0.2 Comprehensions — build a collection in one line

squares = \[n \* n for n in range(5)\] \# \[0, 1, 4, 9, 16\]

evens = \[n for n in range(10) if n % 2 == 0\] \# with a filter

name_to_age = {s\["name"\]: s\["age"\] for s in students} \# dict comprehension

## 0.3 Functions — flexible arguments

def greet(name, greeting="Hello"): \# default argument

return f"{greeting}, {name}"

def total(\*numbers): \# \*args: any number of positional args

return sum(numbers)

def make_user(\*\*fields): \# \*\*kwargs: any number of named args

return fields

greet("Ali") \# Hello, Ali

greet("Ali", greeting="Hi") \# Hi, Ali (keyword argument)

total(1, 2, 3) \# 6

make_user(name="Ali", age=17) \# {'name': 'Ali', 'age': 17}

## 0.4 Decorators — a function that wraps another

You saw @property, @classmethod, @staticmethod. A decorator adds behaviour around a function without changing its body:

import functools

def log_calls(func):

@functools.wraps(func)

def wrapper(\*args, \*\*kwargs):

print(f"calling {func.\_\_name\_\_}")

return func(\*args, \*\*kwargs)

return wrapper

@log_calls

def add(a, b):

return a + b

add(2, 3) \# prints "calling add", returns 5

@log_calls above add means "wrap add with log_calls." **This is exactly how FastAPI's** @app.get("/") **works** — a decorator registering your function as a route.

## 0.5 Type hints — say what goes in and comes out

def average(numbers: list\[float\]) -\> float \| None:

if not numbers:

return None

return sum(numbers) / len(numbers)

Python doesn't enforce these at runtime — they're for editors, for readers, and for tools like mypy. But pydantic and FastAPI **do** enforce them, which is why they matter now.

## 0.6 Exceptions

try:

age = int(user_input)

except ValueError:

print("not a number")

else:

print("got", age) \# runs if no exception

finally:

print("always runs") \# cleanup

### Exercise 0

In essentials.py, write: 1. A function word_count(text: str) -\> dict\[str, int\] that returns how many times each word appears. Use a dict. 2. A function only_adults(people: list\[dict\]) -\> list\[dict\] that returns people with age \>= 18, using a **comprehension**. 3. A decorator timer that prints how long the decorated function took to run (import time, time.perf_counter()). 4. Type hints and a docstring on every function.

# PART 1 — HTTP Fundamentals

Everything web (and every AI API call) is HTTP: a **client** sends a **request**, a **server** sends back a **response**.

**A request has:** - a **method** — GET (read), POST (create), PUT/PATCH (update), DELETE (remove) - a **URL** — https://api.example.com/users/5?active=true - path: /users/5 · query string: ?active=true - **headers** — metadata (e.g. Content-Type: application/json) - optionally a **body** — usually JSON, for POST/PUT

**A response has:** - a **status code** — 200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 404 Not Found, 500 Server Error - **headers** - a **body** — usually JSON

The number ranges matter: **2xx** = success, **4xx** = *you* (the client) did something wrong, **5xx** = the *server* broke.

### Exercise 1 (no code — understanding)

In http_notes.md, answer: 1. You want to *fetch* a list of products. Which method and what status code do you expect? 2. You *submit* a signup form. Which method? What status code means it worked? 3. What's the difference between a 404 and a 500? 4. In https://api.store.com/orders/42?status=open — what is the path, and what is the query parameter?

# PART 2 — Calling APIs from Python (httpx)

Before you *build* an API, consume one. httpx sends HTTP requests from Python.

import httpx

response = httpx.get("https://jsonplaceholder.typicode.com/users/1")

print(response.status_code) \# 200

data = response.json() \# parse JSON body into a Python dict

print(data\["name"\])

\# always check before trusting the body:

if response.status_code == 200:

print(data\["email"\])

else:

print("request failed:", response.status_code)

A POST with a JSON body:

new_post = {"title": "Hello", "body": "World", "userId": 1}

r = httpx.post("https://jsonplaceholder.typicode.com/posts", json=new_post)

print(r.status_code) \# 201 Created

print(r.json())

### Exercise 2

In fetch.py (uses the free https://jsonplaceholder.typicode.com API — needs internet): 1. Fetch user 1 and print their name, email, and city (data\["address"\]\["city"\]). 2. Fetch all posts (/posts), and print **how many** there are. 3. Print the titles of only the posts where userId == 1 (use a comprehension). 4. Wrap each call in a check: if the status code isn't 200, print an error instead of crashing.

# PART 3 — async / await

**The problem it solves:** when your code waits on the network (an API call, a database query), normal ("synchronous") code sits idle doing nothing. async lets your program do *other* work during that wait. FastAPI is built on this.

**Synchronous** — three 1-second calls take 3 seconds, one after another:

import time

def fetch(n):

time.sleep(1) \# pretend this is a slow network call

return n

start = time.perf_counter()

results = \[fetch(1), fetch(2), fetch(3)\]

print(results, time.perf_counter() - start) \# ~3.0 seconds

**Asynchronous** — the same three, overlapped, take ~1 second:

import asyncio, time

async def fetch(n): \# 'async def' makes this a coroutine

await asyncio.sleep(1) \# 'await' = pause here, let others run

return n

async def main():

start = time.perf_counter()

results = await asyncio.gather(fetch(1), fetch(2), fetch(3)) \# run concurrently

print(results, time.perf_counter() - start) \# ~1.0 second

asyncio.run(main()) \# this starts the event loop

Key ideas: - async def defines a **coroutine** — calling it doesn't run it, it returns a coroutine object. - await means "pause here until this finishes, and let other tasks use the time." - asyncio.gather(...) runs many coroutines **concurrently** — this is where the speedup comes from. - asyncio.run(main()) starts everything. - **Trap:** never put a *blocking* call (like time.sleep() or plain httpx.get()) inside async def — it freezes everything. Use the async versions (asyncio.sleep, httpx.AsyncClient).

### Exercise 3

In async_fetch.py, using httpx.AsyncClient: 1. Write an async function that fetches one user by id and returns their name. 2. Fetch users 1 through 5 **concurrently** with asyncio.gather and print all their names. 3. Time it, and compare to fetching them one-by-one in a normal loop. Write the two timings in a comment.

\# starter:

import asyncio, httpx

async def get_user_name(client, user_id):

r = await client.get(f"https://jsonplaceholder.typicode.com/users/{user_id}")

return r.json()\["name"\]

async def main():

async with httpx.AsyncClient() as client:

names = await asyncio.gather(\*\[get_user_name(client, i) for i in range(1, 6)\])

print(names)

asyncio.run(main())

**One honest note:** on a fast test API, the concurrent version can sometimes look no faster (or even slower) than the sequential one, because connection setup overhead swamps the tiny real wait. That's not a sign async failed — it's a sign the wait was too short to matter. The clean proof is the asyncio.sleep(1) example above: three 1-second waits reliably go from ~3s sequential to ~1s concurrent, because there the wait is real and long. Async saves time by overlapping idle waiting, not by making code run faster — when there's nothing to overlap, there's nothing to save.

# PART 4 — Pydantic (the most important one)

Pydantic validates data using Python type hints. It's the backbone of FastAPI — learn it now and FastAPI will click immediately.

Remember your Assignment 1 validation — all those manual if checks for email, age, grades? Pydantic does that for you, from the types:

from pydantic import BaseModel, field_validator, ValidationError

class Student(BaseModel):

name: str

age: int

email: str

grades: dict\[str, int\] = {}

@field_validator("age")

@classmethod

def check_age(cls, v: int) -\> int:

if not 5 \<= v \<= 25:

raise ValueError("age must be between 5 and 25")

return v

\# It COERCES types where sensible: the string "17" becomes int 17

s = Student(name="Ali", age="17", email="ali@example.com")

print(s.age, type(s.age)) \# 17 \<class 'int'\>

print(s.model_dump()) \# -\> a plain dict, ready for JSON

\# It RAISES a clear error on bad data:

try:

Student(name="Bad", age=99, email="x@e.com")

except ValidationError as e:

print(e.errors()\[0\]\["msg"\]) \# "Value error, age must be between 5 and 25"

Key methods: - Student(\*\*data) or Student.model_validate(data) — build and validate from a dict - student.model_dump() — turn the object back into a dict - field_validator — custom rules beyond the type

The big idea: **you declare the shape once, as a class, and pydantic enforces it everywhere.** This is what a real backend uses instead of scattered if checks.

### Exercise 4

In models.py, rebuild your OOP project's Student as a **pydantic** model: 1. Fields: name (str), age (int), email (str), grades (dict of str→int). 2. A validator that rejects an age outside 5–25. 3. A validator that rejects an email without @. 4. Build one from a dict with model_validate, print model_dump(). 5. Feed it bad data in a try/except ValidationError and print the error. 6. Compare in a comment: how many lines was this vs your earlier hand-written validation?

# PART 5 — The ORM Concept (SQLAlchemy)

You wrote raw SQL last week. An **ORM** (Object-Relational Mapper) lets you work with database rows as **Python objects** instead of SQL strings. This connects your OOP week to your SQL week: **a class maps to a table, an object maps to a row.**

from sqlalchemy import create_engine, String, select

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

class Base(DeclarativeBase):

pass

class Book(Base): \# this class...

\_\_tablename\_\_ = "books" \# ...maps to this table

id: Mapped\[int\] = mapped_column(primary_key=True)

title: Mapped\[str\] = mapped_column(String(100))

author: Mapped\[str\] = mapped_column(String(100))

engine = create_engine("sqlite:///library.db") \# the database file

Base.metadata.create_all(engine) \# creates the table

\# INSERT — no SQL, just Python objects:

with Session(engine) as session:

session.add(Book(title="Fluent Python", author="Ramalho"))

session.commit()

\# SELECT — returns objects:

with Session(engine) as session:

books = session.scalars(select(Book)).all()

for book in books:

print(book.id, book.title, book.author)

Notice: no INSERT INTO or SELECT \* FROM strings. You add an *object*; you get *objects* back. The ORM writes the SQL for you. (You still need your SQL knowledge — to understand what it's doing and to debug it.)

### Exercise 5

In library.py: 1. Define a Book model (id, title, author, year). 2. Create the SQLite database and table. 3. Insert 3 books. 4. Query and print all books. 5. Query and print only books after a certain year (look up select(Book).where(Book.year \> 2000)).

## MINI CAPSTONE — tie it all together

In capstone.py, write **one async script** that:

1.  **Fetches** 5 users concurrently from https://jsonplaceholder.typicode.com/users (Part 2 + 3).

2.  **Validates** each into a pydantic User model with fields name, email, city — raising on bad data (Part 4).

3.  **Stores** the validated users in a SQLite database via SQLAlchemy (Part 5).

4.  **Reads them back** from the database and prints them.

This is, in miniature, exactly what a real backend does: fetch → validate → persist → retrieve. Everything after this — FastAPI, then AI features — is a bigger version of this same pipeline.

## What "done well" looks like

| Area               | Full marks                                                                                                                                                       |
|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Part 0             | Comprehensions and a working decorator; type hints + docstrings throughout                                                                                       |
| HTTP understanding | Correct methods/status codes; can name path vs query                                                                                                             |
| httpx              | Handles non-200 responses instead of crashing                                                                                                                    |
| async              | gather genuinely runs concurrently; understands why time.sleep would break it                                |
| pydantic           | Validators work; uses model_validate/model_dump; sees it replaces manual if checks |
| ORM                | Class→table, object→row; insert and filtered query both work                                                                                                     |
| Capstone           | The four stages connect end to end and run without crashing                                                                                                      |

## Review questions (come ready to answer)

- "Why does asyncio.gather make three network calls faster, but wouldn't help three heavy math calculations?"

- "What happens if you call plain httpx.get() (not the async client) inside an async def?"

- "How is a pydantic model different from your earlier hand-written validation? What does it save you?"

- "In the ORM, what is the class, what is the object, and what is the row?"

- "Walk me through your capstone: where does validation happen, and what would break if the API returned a user with no email?"

## After this

Next stop is **FastAPI** — and you'll find it's mostly *these exact pieces combined*: pydantic models for the data, async def for the handlers, and functions registered with decorators. You've already learned the hard parts.
