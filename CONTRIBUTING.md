# Contributing to ZooStudy

Welcome to ZooStudy! This guide will help you get up to speed quickly and start developing in your assigned area.

---

## What's Already Done

The project skeleton is fully set up and ready for development. Here's what you're working with:

### Models & Database (complete)
All 7 models are implemented with business logic methods. The database layer is ready — you **do not** need to touch `models.py` unless we agree on a schema change as a team.

### Placeholder Views & Templates
Every page has a placeholder view in `views.py` and a template in `templates/zoo_app/`. They all work — you can visit every URL right now. Your job is to replace the `TODO` placeholders with real functionality.

### Population Script
Run `python population_script.py` to fill the database with test data: 12 animals, 3 users, 11 tasks, 15 study sessions, and 12 notes/resources. Use these to test your work.

### Test Accounts
After running the population script, you can log into these accounts:

| Username | Password | Profile |
|----------|----------|---------|
| `daniel_m` | `testpass123` | Power user: 25-day streak, 3 animals, 5 tasks |
| `sofia_d` | `testpass123` | Moderate user: 7-day streak, 1 animal, 3 tasks |
| `carl_j` | `testpass123` | New user: 3-day streak, 0 animals, 3 tasks (1 overdue) |

---

## Available Model Methods

These are the methods you can call directly from views and templates. **You don't need to rewrite any of this logic.**

### UserProfile (`request.user.userprofile`)

| Method | What it does | Returns | Example usage |
|--------|-------------|---------|---------------|
| `add_currency(minutes)` | Converts study time to coins (10 coins/min) and adds to balance | `int` (coins earned) | `coins = profile.add_currency(60)` |
| `update_streak()` | Updates streak: +1 if consecutive day, reset if missed | — | `profile.update_streak()` |
| `buy_animal(animal)` | Checks balance, deducts cost, creates UserZoo entry | `(bool, str)` — (success, message) | `success, msg = profile.buy_animal(animal)` |
| `owns_animal(animal)` | Checks if user already owns this animal | `bool` | `if profile.owns_animal(animal):` |
| `total_study_minutes()` | Sum of all study session durations | `int` | `mins = profile.total_study_minutes()` |
| `total_study_hours()` | Total study time in hours (1 decimal) | `float` | `hours = profile.total_study_hours()` |
| `zoo_animal_count()` | Number of animals user owns | `int` | `count = profile.zoo_animal_count()` |

### Task

| Property | What it does | Returns |
|----------|-------------|---------|
| `is_overdue` | Deadline passed and not completed? | `bool` |
| `time_remaining` | Time left until deadline | `timedelta` or `None` |
| `time_remaining_display` | Human-readable string | `str` like `"3d 2h"`, `"45m"`, or `"Overdue"` |

### StudySession

| Method / Property | What it does | Returns |
|-------------------|-------------|---------|
| `StudySession.log_session(user, minutes)` | **One-stop method**: creates session + adds coins + updates streak | `(session, coins_earned)` |
| `coins_earned` | How many coins this session was worth | `int` |
| `duration_display` | Human-readable duration | `str` like `"1h 30m"` |

### Animal

| Property | What it does | Returns |
|----------|-------------|---------|
| `study_hours_required` | Hours of study needed to afford this animal | `float` |

### Game Constants (defined at top of `models.py`)

| Constant | Value | Meaning |
|----------|-------|---------|
| `COINS_PER_MINUTE` | 10 | 1 minute of study = 10 coins |
| `STREAK_MINIMUM_MINUTES` | 15 | Must study at least 15 min to keep streak alive |

---

## Guide by Role

### Area B: User Auth & Testing

**Your files:** `views.py` (login/register/logout), `forms.py`, `tests.py`

**What's ready for you:**
- `UserForm` and `UserProfileForm` in `forms.py` — registration forms are defined
- `user_login`, `register`, `user_logout` views exist as placeholders
- `@login_required` decorators already on all protected views
- `LOGIN_URL = '/login/'` configured in settings

**Your first tasks:**
1. Implement the `register` view — handle POST with `UserForm`, create User + UserProfile, log them in, redirect to dashboard
2. Implement `user_login` — authenticate, login, redirect to dashboard
3. Start writing unit tests — test that models create correctly, views return correct status codes, unauthenticated users get redirected

**Key code pattern for registration:**
```python
def register(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('zoo_app:dashboard')
    else:
        user_form = UserForm()
    return render(request, 'zoo_app/register.html', {'form': user_form})
```

---

### Area C: Views & URLs

**Your files:** `views.py` (all views except auth), `urls.py`

**What's ready for you:**
- All URL patterns defined in `urls.py`
- All views exist as placeholders — just add logic
- Model methods handle all business logic — you just call them

**Your first tasks:**
1. Implement `dashboard` view — query user stats and pass to template
2. Implement `study_hub` view — list tasks, handle task creation with `TaskForm`
3. Implement `shop` view — list animals, handle purchase

**Key code patterns:**

Dashboard view:
```python
@login_required
def dashboard(request):
    profile = request.user.userprofile
    context = {
        'total_hours': profile.total_study_hours(),
        'currency': profile.currency,
        'streak': profile.streak,
        'animal_count': profile.zoo_animal_count(),
        'recent_tasks': Task.objects.filter(user=request.user, completed=False)[:5],
    }
    return render(request, 'zoo_app/dashboard.html', context)
```

Animal purchase (for AJAX — work with Area E):
```python
@login_required
def buy_animal(request, slug):
    animal = get_object_or_404(Animal, slug=slug)
    profile = request.user.userprofile
    success, message = profile.buy_animal(animal)
    return JsonResponse({'success': success, 'message': message, 'currency': profile.currency})
```

---

### Area D: Templates & CSS

**Your files:** `templates/zoo_app/*.html`, `static/zoo_app/css/style.css`

**What's ready for you:**
- `base.html` with Bootstrap 5, jQuery, navbar (login-aware), footer
- 8 page templates inheriting from base — replace the TODO content
- `static/zoo_app/css/style.css` for custom styles
- Wireframes in the Design Spec for layout reference

**Your first tasks:**
1. Style the home page — welcome message, login/register buttons, zoo-themed design
2. Style the login and register pages — form layout with Bootstrap
3. Design the dashboard layout — progress bar, currency display, streak counter, quick nav cards

**Template tips:**
- All templates already extend `base.html` — just fill in `{% block content %}`
- Access user data passed from views: `{{ total_hours }}`, `{{ currency }}`, `{{ streak }}`
- Check authentication: `{% if user.is_authenticated %}`
- Use the `{% url 'zoo_app:page_name' %}` tag for all links
- Keep CSS in `style.css`, JS in `main.js` — not inline

---

### Area E: JavaScript/AJAX & Deployment

**Your files:** `static/zoo_app/js/main.js`, PythonAnywhere config

**What's ready for you:**
- jQuery loaded in `base.html`
- `main.js` included on every page via base template
- `{% block extra_js %}` available for page-specific scripts

**Your first tasks:**
1. Build the study timer (start/pause/stop, sends duration to backend via AJAX)
2. Set up a PythonAnywhere account and do a test deployment
3. Later: AJAX animal purchase, task completion toggle without page refresh

**AJAX pattern:**
```javascript
// Example: log a study session
$.ajax({
    url: '/study/log/',
    type: 'POST',
    data: {
        duration_minutes: totalMinutes,
        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
    },
    success: function(response) {
        // response.coins_earned, response.new_balance, response.streak
        $('#currency-display').text(response.new_balance);
    }
});
```

---

## File Dependency Map

```
Who can start immediately (no dependencies):
  ✅ Area B (Auth & Testing) — forms are ready
  ✅ Area D (Templates & CSS) — base.html is ready
  ✅ Area E (JS/AJAX) — jQuery is loaded, can build timer standalone

Who needs light coordination:
  ⏳ Area C (Views) — can start dashboard/study_hub now,
                       needs Area B's auth working for full testing

Merge order recommendation:
  1. Area B (auth) → everyone can test with real login
  2. Area C (views) → templates get real data
  3. Area D (templates) → pages look good
  4. Area E (JS/AJAX) → interactivity layer on top
```

---

## Quick Reference

### Common Commands
```bash
python manage.py runserver          # Start dev server
python manage.py makemigrations     # After model changes
python manage.py migrate            # Apply migrations
python population_script.py         # Fill database with test data
python manage.py createsuperuser    # Create admin account
python manage.py test               # Run unit tests
```

### Admin Panel
Visit `http://127.0.0.1:8000/admin/` to browse and edit all data directly. Create a superuser first.

### Git Workflow Reminder
```bash
git checkout feature/your-branch    # Work on your branch
git add .
git commit -m "feat: description"   # Use commit prefixes
git push origin feature/your-branch # Push to GitHub
# Then create Pull Request on GitHub to merge into main
```

---

Questions? Ask in the Teams group chat. Let's build a great app!
