# Django Task Manager

A small slice of my FastAPI Task API, rebuilt in Django 4.2 with Django REST Framework. Same idea (tasks that belong to a user), second framework.

## What is in it
- A `Task` model with an owner (Django's built-in `User`), migrated with `makemigrations` and `migrate`
- An admin panel with columns, filters, search, an editable "done" checkbox, newest-first ordering and a bulk action "Mark selected tasks as done"
- A DRF API (`/api/tasks/`) with full CRUD, login required, and each user only sees their own tasks

## How to run it
1. `python -m venv .venv` then activate it
2. `pip install -r requirements.txt`
3. `python manage.py migrate`
4. `python manage.py createsuperuser`
5. `python manage.py runserver`

Admin: http://127.0.0.1:8000/admin/ . API: http://127.0.0.1:8000/api/tasks/

## How I checked that users only see their own tasks
I made two users, alice (2 tasks) and bob (1 task). Without login the API gave 403. alice got her 2 tasks, bob got only his 1. When bob asked for alice's task by id, he got 404. A task alice created through the API showed up only in her list.

## Django vs FastAPI (from my own experience)

**Development speed.** Django was faster to get a working CRUD API. The model, migrations, user table and admin panel were ready in a few commands. In FastAPI I wrote the password hashing, JWT and database setup myself, so it took much longer.

**What I got for free, and what it cost.** Django gave me users and login, the ORM, migrations and the admin panel. The cost is control and visibility: I did not see how passwords or sessions work, because Django hides it. In FastAPI I understand every line of auth because I wrote it, but I also had to write it.

**Ownership check.** In FastAPI I checked the owner myself and returned 403. In Django one line, `Task.objects.filter(owner=self.request.user)` in `get_queryset`, does the same job, but another user's task gives 404 instead of 403. Same idea, different spelling.

**Admin panel.** It is a real advantage for an internal tool, where staff need to edit data without writing a frontend. It is the wrong tool for customers, because it is for trusted internal users and it is not a public API.

**One practical note.** My laptop has Python 3.9, which cannot run Django 5.2 (needs 3.10+), so I used Django 4.2 LTS. Everything in the handout worked the same.


## Knowledge app (RAG, fully local)

A small question-answering feature over my own handouts. It splits documents into chunks, turns each chunk into an embedding (nomic-embed-text through Ollama), finds the chunks closest to a question, and asks llama3.2 (also through Ollama) to answer using only those chunks. Nothing is trained, and no API key is needed.

### How to run it
1. Install Ollama, then `ollama pull llama3.2` and `ollama pull nomic-embed-text`. Keep `ollama serve` running.
2. `pip install -r requirements.txt`
3. `python manage.py migrate`
4. `python manage.py ingest docs`
5. `python manage.py runserver` and open `/ask/?q=What does DefaultRouter do`

Tests: `python manage.py test knowledge`. They do not need Ollama, because `embed` and `generate` are mocked.

### Did I check that the answers are right?
I asked three real questions and compared each answer with the handout:
1. "What does DefaultRouter do?" The answer was correct. But the sources list also showed an unrelated document, so the sources show which documents were retrieved, not which ones the answer really used.
2. "Why does the Dockerfile copy requirements.txt before the rest of the code?" Mostly correct (layer caching), but the model dropped the condition that this only matters if the code is copied first.
3. "What is the difference between WHERE and HAVING?" The answer was "I do not know". The explanation is in the handout, but retrieval found a chunk that only contained the review question with the same words, not the explanation. So retrieval failed, while grounding worked: the model said it did not know instead of inventing an answer.

I also tried k=6 instead of k=3. It did not fix question 3, and it made question 2 worse ("I do not know"), because more chunks also meant more irrelevant text for a small 2GB model. So a bigger k is not a fix. A better fix would be better chunking (for example keeping the section heading with each chunk and keeping code blocks whole).