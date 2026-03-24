# 🦁 ZooStudy

A gamified study tracking web application where your study hours build your very own zoo!

## Overview

ZooStudy is a Django-based web application designed to motivate students by turning study time into a rewarding experience. Users track their study hours using a built-in timer, which converts into in-game currency. This currency can then be used to unlock and collect animals for a personal zoo — a visual representation of their hard work and dedication.

The app also provides practical study tools including task management with deadlines, a study session log, and a notes & resources section to help students stay organised.

## Features

- **User Authentication** — Register, login, and manage your profile
- **Dashboard** — View total study time, currency balance, study streak, and quick navigation
- **Study Hub** — Create tasks with deadlines, log study sessions with a timer
- **Zoo Page** — Display your collected animals, organised by habitat categories
- **Animal Shop** — Browse and purchase animals using earned currency
- **Notes & Resources** — Store notes and useful links for each task

## Tech Stack

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, Bootstrap 5
- **Interactivity:** JavaScript, jQuery, AJAX
- **Database:** SQLite
- **Deployment:** PythonAnywhere

## Data Models

| Model | Description |
|-------|-------------|
| User | Django built-in authentication model |
| UserProfile | Extends User with currency, streak, last study date |
| Task | User's study tasks with titles and deadlines |
| StudySession | Records of individual study sessions (duration, date) |
| Animal | Available animals with name, category, cost, and image |
| UserZoo | Tracks which animals a user has acquired |
| Resource/Notes | Notes and resource links attached to tasks |

## Project Structure

```
zoo_study_project/
├── zoo_study/              # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── zoo_app/                # Main application
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── forms.py
│   ├── tests.py
│   ├── templates/
│   │   └── zoo_app/
│   │       ├── base.html
│   │       ├── home.html
│   │       ├── login.html
│   │       ├── register.html
│   │       ├── dashboard.html
│   │       ├── zoo.html
│   │       ├── shop.html
│   │       ├── study_hub.html
│   │       └── notes.html
│   └── static/
│       └── zoo_app/
│           ├── css/
│           ├── js/
│           └── images/
├── population_script.py
├── requirements.txt
├── manage.py
└── README.md
```

## URL Map

| URL | Page |
|-----|------|
| `/` | Home |
| `/login/` | Login |
| `/register/` | Register |
| `/dashboard/` | User Dashboard |
| `/zoo/` | My Zoo |
| `/zoo/shop/` | Animal Shop |
| `/study/` | Study Hub |
| `/study/notes/` | Notes & Resources |

---

## Team — Lab Group 6A

| Member | Role |
|--------|------|
| Jasper | Area A — Models & Database; Final code integration |
| Abdul | Area B — User Auth & Testing |
| Frank | Area C — Views & URLs |
| Noor | Area D — Templates & CSS |
| Bonnie | Area E — JavaScript/AJAX & Deployment |

### Role Divisions

The project is divided into 5 areas of responsibility. Each team member owns one area:

| # | Area | Scope |
|---|------|-------|
| A | **Models & Database** | `models.py`, `admin.py`, `population_script.py`, database design |
| B | **User Auth & Testing** | Registration, login/logout, `@login_required`, unit tests in `tests.py` |
| C | **Views & URLs** | All view functions in `views.py`, URL routing in `urls.py`, form handling |
| D | **Templates & CSS** | All HTML templates, `base.html`, Bootstrap styling, responsive design |
| E | **JavaScript/AJAX & Deployment** | jQuery interactions, AJAX calls, study timer, PythonAnywhere deployment |

> Role assignments will be confirmed at our team kickoff meeting.

---

## Git Workflow

### Branches

Each team member works on their own branch based on their role:

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready code only — **never push directly to main** |
| `feature/models-database` | Area A: Models & Database |
| `feature/auth-testing` | Area B: User Auth & Testing |
| `feature/views-urls` | Area C: Views & URLs |
| `feature/templates-css` | Area D: Templates & CSS |
| `feature/js-ajax-deploy` | Area E: JavaScript/AJAX & Deployment |

**Workflow:**
1. Always pull the latest `main` before starting work: `git pull origin main`
2. Switch to your branch: `git checkout feature/your-branch`
3. Merge latest main into your branch: `git merge main`
4. Work, commit, push to your branch
5. When a feature is complete, create a **Pull Request** on GitHub to merge into `main`
6. At least one other team member should review before merging

### Commit Message Convention

Use standardised prefixes so our commit history stays readable:

| Prefix | When to Use | Example |
|--------|-------------|---------|
| `feat:` | New feature | `feat: add study timer to study hub page` |
| `fix:` | Bug fix | `fix: correct currency calculation after purchase` |
| `style:` | CSS/UI changes (no logic change) | `style: update navbar colour scheme` |
| `docs:` | Documentation | `docs: update README with role assignments` |
| `test:` | Adding or updating tests | `test: add unit tests for Animal model` |
| `refactor:` | Code restructuring (no new feature) | `refactor: extract helper function for streak calculation` |
| `chore:` | Config, dependencies, setup | `chore: add Pillow to requirements.txt` |

**Format:** `prefix: short description in lowercase`

**Examples:**
```
feat: add animal purchase AJAX endpoint
fix: resolve login redirect loop
style: centre zoo grid on mobile
docs: add deployment instructions
test: add view tests for dashboard
```

---

## Getting Started

### Prerequisites
- Python 3.x
- pip

### Setup
```bash
# Clone the repository
git clone https://github.com/Ddddd917/Zoo_Study.git
cd Zoo_Study

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations zoo_app
python manage.py migrate

# Populate the database with sample data
python population_script.py

# Start the development server
python manage.py runserver
```

Then visit `http://127.0.0.1:8000/` in your browser.

## Deployment

The app is hosted on PythonAnywhere:
**URL:** `TBD`

---

## External Sources & Acknowledgements

| Resource | Usage |
|----------|-------|
| [Django](https://www.djangoproject.com/) | Web framework |
| [Bootstrap 5](https://getbootstrap.com/) | Responsive CSS framework |
| [jQuery](https://jquery.com/) | JavaScript library for AJAX and DOM manipulation |
| [Pillow](https://python-pillow.org/) | Image handling for animal images |

> Additional external sources will be documented here as development progresses.

---

University of Glasgow — Web Application Development 2 (2025-26)