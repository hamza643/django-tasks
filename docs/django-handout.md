# Django & the Admin Panel — Same Problems, Different Tool

**Where you are:** you've built a real FastAPI backend — routing, pydantic, auth, an ORM, tests, Docker. This isn't a second track starting from zero; it's a **bounded, focused detour** to see how a different, hugely popular framework solves the exact same problems you've already solved — and to get hands-on with the one thing FastAPI genuinely doesn't have: **a free, fully working admin interface.**

**Why this is worth a week, not a month:** Django and FastAPI both handle requests, models, and databases — you already understand *what* needs to happen; this is about *how Django's conventions differ*. So this handout moves fast through the parts that map directly onto what you know, and slows right down for the admin panel, which is genuinely new and genuinely useful.

**The rebuild, deliberately:** you're going to rebuild a small slice of your **Task API** — the exact same domain — in Django. Same problem, second tool. That makes the comparison concrete instead of abstract.

**How to use this:** **Read → Run → Do**, as always. Every command and file here was built and tested before being written down.

## Setup

mkdir django-tasks && cd django-tasks

py -m venv .venv

.\\venv\Scripts\Activate.ps1

pip install "django==5.2.\*" djangorestframework

pip freeze \| Out-File -Encoding utf8 requirements.txt

# PART 1 — Project structure: Django's conventions vs. FastAPI's

django-admin startproject taskproject .

python manage.py startapp tasks

This creates:

django-tasks/

├── manage.py \# your command-line tool: runserver, migrate, etc.

├── taskproject/ \# the PROJECT — overall settings, root URLs

│ ├── settings.py

│ └── urls.py

└── tasks/ \# an APP — one self-contained feature area

├── models.py

├── admin.py

├── views.py

└── migrations/

**The mental mapping to what you know:**

| FastAPI                           | Django                                                                                                                                 |
|-------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| main.py + routers/                | taskproject/urls.py (root) + each app's own urls.py                                                                                    |
| a pydantic model in schemas.py    | a Serializer in serializers.py (Part 5)                                                                                                |
| a SQLAlchemy model in database.py | a Model in models.py                                                                                                                   |
| Depends(get_db) per request       | Django's ORM manages connections for you, no explicit dependency                                                                       |
| one flat project                  | **project** (settings, root config) containing multiple **apps** (features) — Django expects you to split by feature area from day one |

A Django **project** is the whole site; an **app** is one feature within it (here: tasks). A real Django site might have tasks, users, billing as separate apps inside one project — this is Django's built-in version of the routers-and-services split you already do by convention in FastAPI.

### Do it

Run python manage.py runserver and open http://127.0.0.1:8000/ — Django's default "it worked" page. Confirm it starts with zero configuration.

# PART 2 — Models: the same ORM idea, different syntax

Register your app first — add "tasks" to INSTALLED_APPS in taskproject/settings.py. **This step has no FastAPI equivalent, and it's the single most common thing beginners forget** — an app with no model registered anywhere Django will actually run migrations for.

\# tasks/models.py

from django.db import models

from django.contrib.auth.models import User

class Task(models.Model):

PRIORITY_CHOICES = \[(1, "Low"), (2, "Medium"), (3, "High")\]

title = models.CharField(max_length=100)

description = models.TextField(blank=True)

priority = models.IntegerField(choices=PRIORITY_CHOICES, default=1)

due_date = models.DateField(null=True, blank=True)

done = models.BooleanField(default=False)

owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")

created_at = models.DateTimeField(auto_now_add=True)

def \_\_str\_\_(self):

return self.title

Compare this to your SQLAlchemy TaskRow — same idea, different spelling: CharField instead of Mapped\[str\] = mapped_column(String(...)), ForeignKey works the same way, and \_\_str\_\_ is Django's equivalent of \_\_repr\_\_ — it's what shows up when an object is printed, and critically, **it's what the admin panel displays for this object**, which matters a lot in Part 4.

**The built-in** User **model** is worth pausing on: Django ships with a full user model, password hashing, and authentication out of the box. You built all of that by hand in FastAPI (bcrypt, JWT, UserRow) — here it's already done for you. That's a real trade-off to notice: less code to write, less control over exactly how it works.

### Migrations — Django's Alembic, built in

python manage.py makemigrations tasks

python manage.py migrate

makemigrations looks at your models and generates a migration file describing the change; migrate applies it to the database. This is the same job Alembic does for SQLAlchemy, except it's part of Django itself rather than a separate library you add.

### Do it

Create the Task model above, register the app, run both migration commands, and confirm tasks/migrations/0001_initial.py was generated.

# PART 3 — The Django shell: poking at your data directly

python manage.py shell

from django.contrib.auth.models import User

from tasks.models import Task

user = User.objects.create_user("alice", password="secret123")

Task.objects.create(title="Try the Django shell", priority=2, owner=user)

Task.objects.filter(owner=user) \# Django's query syntax

Task.objects.filter(done=False).count()

This is Django's equivalent of a Python REPL with your models already imported and your database already connected — genuinely handy for quick checks, seeding test data, or debugging, without writing a script or hitting an endpoint.

### Do it

Create two users and a couple of tasks each via the shell. Practice .filter(), .count(), and .get().

# PART 4 — The Admin Panel (the main event)

This is the feature that has no FastAPI equivalent, and it's a genuine reason some teams choose Django. In three lines, you get a full, working, permission-aware web interface for managing your data — no frontend code, nothing.

\# tasks/admin.py

from django.contrib import admin

from .models import Task

@admin.register(Task)

class TaskAdmin(admin.ModelAdmin):

list_display = ("title", "owner", "priority", "due_date", "done")

list_filter = ("done", "priority")

search_fields = ("title", "description")

list_editable = ("done",)

python manage.py createsuperuser

python manage.py runserver

Open http://127.0.0.1:8000/admin/, log in, and click into **Tasks**. What you get, from those five lines:

- list_display — which columns show in the table (I verified this exact config produces a table with Title / Owner / Priority / Due date / Done columns)

- list_filter — a sidebar to filter by status or priority with one click

- search_fields — a working search box across those fields

- list_editable — tick a task done directly from the list, no separate edit page

**Why this matters in the real world:** this is how non-technical staff manage data without touching code or calling an API — customer support marking orders as resolved, an editor publishing blog posts, an ops person adjusting inventory. You'd otherwise have to *build* an internal tool to do this. Django gives it to you for free, wired directly to your real models and your real database.

**The honest trade-off:** the admin panel is for *internal* users you trust with direct data access, not a customer-facing UI, and it doesn't replace a real frontend or a public API. It's a tool for the people running the system, not the people using it.

### Do it

Configure the admin exactly as above, create a superuser, log in, and use the search box and the done checkbox toggle directly from the list view. Then customize it further: change list_display to also show created_at, and add ordering = \["-created_at"\] to the TaskAdmin class so newest tasks show first.

# PART 5 — A real API with Django REST Framework (DRF)

Django's raw views can return HTML or JSON manually, but **DRF** is the standard way to build a proper API on top of Django models — the closest thing to what FastAPI gives you natively.

\# tasks/serializers.py

from rest_framework import serializers

from .models import Task

class TaskSerializer(serializers.ModelSerializer):

class Meta:

model = Task

fields = \["id", "title", "description", "priority", "due_date", "done", "owner"\]

read_only_fields = \["owner"\]

A Serializer is DRF's version of your pydantic Task/TaskCreate schemas — it defines what fields come in and out, and validates them.

\# tasks/views.py

from rest_framework import viewsets, permissions

from .models import Task

from .serializers import TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):

serializer_class = TaskSerializer

permission_classes = \[permissions.IsAuthenticated\]

def get_queryset(self):

return Task.objects.filter(owner=self.request.user) \# \<-- look familiar?

def perform_create(self, serializer):

serializer.save(owner=self.request.user)

**Stop on** get_queryset **for a second.** Task.objects.filter(owner=self.request.user) is doing *exactly* the same job as .where(TaskRow.user_id == user.id) in your FastAPI routes — restricting every query to the logged-in user's own data. I tested this directly: a second user hitting this endpoint got back an empty list, never seeing the first user's task. **Same security requirement, same underlying idea, different framework's syntax.** This is the single clearest proof that the concepts transfer — you're not relearning the idea, only the spelling.

A ViewSet bundles list/create/retrieve/update/delete into one class — DRF's answer to writing five separate route functions.

\# taskproject/urls.py

from django.contrib import admin

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from tasks.views import TaskViewSet

router = DefaultRouter()

router.register("tasks", TaskViewSet, basename="task")

urlpatterns = \[

path("admin/", admin.site.urls),

path("api/", include(router.urls)),

\]

DefaultRouter auto-generates the URLs a ViewSet needs (list, detail, create, update, delete) — you register the viewset once instead of writing @app.get, @app.post, etc. individually.

### Do it

Add "rest_framework" to INSTALLED_APPS, wire up the serializer/viewset/router above, and test it: an unauthenticated request should be rejected, and two different logged-in users should each see only their own tasks — confirm this the same way you'd test the permission boundary in your FastAPI project.

# PART 6 — The comparison (the actual point of this module)

You've now built the same small feature twice. Answer this honestly, in writing, in your README:

- **Development speed** — which was faster to get a working CRUD API running from zero?

- **What you got for free** — auth, the ORM, the admin panel, migrations: which framework gives you more out of the box, and what did that cost you in flexibility?

- **Async** — FastAPI is async-first; Django's traditional views are synchronous (async support exists but isn't the default mental model). Does that matter for the kind of app you'd build?

- **The admin panel specifically** — where would this be a genuine advantage? Where would it be irrelevant or even the wrong tool?

- **If someone asked you to build an internal tool for a small team to manage inventory, which would you reach for? What about a service other backends call over an API, with no human ever looking at a UI?**

There's no "correct" answer here — the point is that you can now argue the trade-off from real, hands-on experience instead of a tutorial's opinion.

# THE ASSIGNMENT — Task Manager, Django Edition

Rebuild a focused slice of your Task API in Django:

1.  A Task model (as above), properly migrated.

2.  **A fully configured admin panel** — list_display, list_filter, search_fields, and at least one further customization beyond the handout's example (your choice — a custom action, an inline, a computed column).

3.  A DRF API: full CRUD on tasks, authenticated, **scoped to the logged-in user** (verify this the same rigorous way you did in FastAPI — two users, confirm isolation).

4.  Django's built-in User model for auth — no need to rebuild JWT/bcrypt by hand here; use what Django gives you (session or token auth via DRF is fine).

5.  A README.md containing the **Part 6 comparison**, written honestly from your own experience.

**Stretch goals:** - A custom admin action (e.g., "mark selected tasks as done" as a bulk action). - TaskAdmin with an inline showing something related (if you add a Category or Tag model). - DRF token authentication instead of session auth, so the API can be used the way your FastAPI JWT was.

## What "done well" looks like

| Area                | Full marks                                                                             |
|-----------------------------------------------|------------------------------------------------------------------------------------------------------------------|
| Models & migrations | Clean model, migrations generated and applied without manual edits                     |
| Admin panel         | Genuinely useful — configured beyond the bare minimum, and you can explain each option |
| DRF API             | Full CRUD, correctly scoped per user — verified with two real accounts, not assumed    |
| Comparison write-up | Specific and honest, grounded in what you actually built, not generic talking points   |

## Review questions

- "What does get_queryset do here, and what's the FastAPI line that does the same job in your Task API?"

- "Where does Django's User model save you time versus what you built by hand in FastAPI? What do you give up?"

- "Show me your admin panel. Which of the four config options did you find most useful, and why?"

- "If you forgot to add 'tasks' to INSTALLED_APPS, what would break, and how would you notice?"

- "Give me one real scenario where you'd pick Django over FastAPI, and one where you'd pick the reverse."
