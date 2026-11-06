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