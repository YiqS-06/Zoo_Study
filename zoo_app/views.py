from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum
from django.utils import timezone

from zoo_app.models import UserProfile, Task, StudySession, Animal, UserZoo, Resource
from zoo_app.forms import UserRegisterForm, UserLoginForm, TaskForm, ResourceForm
from django.contrib import messages


def home(request):
    """Render the public landing page."""
    return render(request, 'zoo_app/home.html')


def register(request):
    """Handle new user registration; auto-login on success and redirect to dashboard."""
    registered = False

    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            UserProfile.objects.create(user=user)

            registered = True
            login(request, user)
            return redirect('zoo_app:dashboard')
    else:
        user_form = UserRegisterForm()

    return render(request, 'zoo_app/register.html', {'user_form': user_form, 'registered': registered})


def user_login(request):
    """Authenticate user credentials and redirect to dashboard on success."""
    if request.method == 'POST':
        login_form = UserLoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']

            user = authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    login(request, user)
                    return redirect('zoo_app:dashboard')
                else:
                    messages.error(request, "Account is inactive.")
            else:
                messages.error(request, "Invalid login details.")
    else:
        login_form = UserLoginForm()
    return render(request, 'zoo_app/login.html', {'login_form': login_form})


@login_required
def user_logout(request):
    """Log the user out and redirect to the home page."""
    logout(request)
    return redirect('zoo_app:home')


@login_required
def dashboard(request):
    """Show the user's summary stats, coin balance, streak, and upcoming tasks."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    total_study_minutes = StudySession.objects.filter(user=request.user).aggregate(
        Sum('duration_minutes')
    )['duration_minutes__sum'] or 0

    hours = total_study_minutes // 60
    minutes = total_study_minutes % 60

    tasks = Task.objects.filter(user=request.user, completed=False).order_by('deadline')

    return render(request, 'zoo_app/dashboard.html', {
        'profile': profile,
        'hours': hours,
        'minutes': minutes,
        'tasks': tasks,
    })


@login_required
def zoo(request):
    """Display the user's owned animals grouped by habitat."""
    user_zoo_entries = UserZoo.objects.filter(user=request.user).select_related('animal')
    my_animals = [entry.animal for entry in user_zoo_entries]

    # Build habitat groups for template: list of (name, emoji, animals)
    habitat_defs = [
        ('forest', '🌲'),
        ('aquatic', '🌊'),
        ('desert', '🏜️'),
        ('polar', '❄️'),
    ]
    habitats = []
    for name, emoji in habitat_defs:
        animals_in = [a for a in my_animals if a.category == name]
        habitats.append({'name': name, 'emoji': emoji, 'animals': animals_in})

    return render(request, 'zoo_app/zoo.html', {
        'my_animals': my_animals,
        'habitats': habitats,
    })


@login_required
def shop(request):
    """List all purchasable animals with the user's current coin balance."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    all_animals = Animal.objects.all().order_by('category', 'cost')
    owned_ids = UserZoo.objects.filter(user=request.user).values_list('animal_id', flat=True)

    return render(request, 'zoo_app/shop.html', {
        'animals': all_animals,
        'profile': profile,
        'owned_ids': owned_ids,
    })


@login_required
def study_hub(request):
    """Show the study timer, task management form, and recent session history."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        task_form = TaskForm(request.POST)
        if task_form.is_valid():
            task = task_form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, "Task created!")
            return redirect('zoo_app:study_hub')
    else:
        task_form = TaskForm()

    tasks = Task.objects.filter(user=request.user).order_by('completed', 'deadline')
    sessions = StudySession.objects.filter(user=request.user).order_by('-date')[:10]

    return render(request, 'zoo_app/study_hub.html', {
        'profile': profile,
        'task_form': task_form,
        'tasks': tasks,
        'sessions': sessions,
    })


@login_required
def notes(request):
    """Display and handle submission of notes/resources linked to the user's tasks."""
    tasks = Task.objects.filter(user=request.user).prefetch_related('resources').order_by('deadline')

    if request.method == 'POST':
        resource_form = ResourceForm(request.POST)
        task_id = request.POST.get('task_id')
        if resource_form.is_valid() and task_id:
            try:
                task = Task.objects.get(id=task_id, user=request.user)
                resource = resource_form.save(commit=False)
                resource.task = task
                resource.save()
                messages.success(request, "Note saved!")
                return redirect('zoo_app:notes')
            except Task.DoesNotExist:
                pass
    else:
        resource_form = ResourceForm()

    return render(request, 'zoo_app/notes.html', {
        'tasks': tasks,
        'resource_form': resource_form,
    })


# ======== AJAX ENDPOINTS ========

@login_required
@require_POST
def buy_animal(request):
    """AJAX: deduct coins and add animal to user's zoo. Returns JSON with updated balance."""
    animal_id = request.POST.get('animal_id')
    try:
        animal = Animal.objects.get(id=animal_id)
        profile = request.user.userprofile
        success, message = profile.buy_animal(animal)
        return JsonResponse({'success': success, 'message': message, 'currency': profile.currency})
    except Animal.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Animal not found'})


@login_required
@require_POST
def log_study_session(request):
    """AJAX: save a completed study session and award coins/streak. Returns JSON with earned coins."""
    duration_minutes = int(request.POST.get('duration_minutes', 0))
    session, coins = StudySession.log_session(request.user, duration_minutes)
    if session:
        profile = request.user.userprofile
        return JsonResponse({
            'success': True,
            'coins_earned': coins,
            'total_currency': profile.currency,
            'streak': profile.streak,
            'duration_display': session.duration_display,
        })
    return JsonResponse({'success': False, 'message': 'Invalid duration'})


@login_required
@require_POST
def toggle_task_complete(request):
    """AJAX: flip a task's completed flag. Returns JSON with the new completed state."""
    task_id = request.POST.get('task_id')
    try:
        task = Task.objects.get(id=task_id, user=request.user)
        task.completed = not task.completed
        task.save()
        return JsonResponse({'success': True, 'completed': task.completed})
    except Task.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Task not found'})
