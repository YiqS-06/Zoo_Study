import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zoo_study.settings')

import django
django.setup()

from django.contrib.auth.models import User
from zoo_app.models import UserProfile, Task, StudySession, Animal, UserZoo, Resource
from datetime import datetime, timedelta
from django.utils import timezone


def populate():
    # --- Animals ---
    # Based on the wireframe: 4 categories, various costs
    animals_data = [
        # Desert animals
        {'name': 'Camel', 'category': 'desert', 'cost': 2000},
        {'name': 'Scorpion', 'category': 'desert', 'cost': 3000},
        {'name': 'Rattlesnake', 'category': 'desert', 'cost': 3500},
        # Aquatic animals
        {'name': 'Dolphin', 'category': 'aquatic', 'cost': 4000},
        {'name': 'Octopus', 'category': 'aquatic', 'cost': 4800},
        {'name': 'Clownfish', 'category': 'aquatic', 'cost': 6000},
        # Forest animals
        {'name': 'Fox', 'category': 'forest', 'cost': 6500},
        {'name': 'Deer', 'category': 'forest', 'cost': 7000},
        {'name': 'Gorilla', 'category': 'forest', 'cost': 7500},
        # Polar animals
        {'name': 'Penguin', 'category': 'polar', 'cost': 8500},
        {'name': 'Polar Bear', 'category': 'polar', 'cost': 9000},
        {'name': 'Snow Leopard', 'category': 'polar', 'cost': 10000},
    ]

    animals = {}
    for a in animals_data:
        animal, created = Animal.objects.get_or_create(
            name=a['name'],
            defaults={'category': a['category'], 'cost': a['cost']}
        )
        animals[a['name']] = animal
        print(f"  {'Created' if created else 'Found'} animal: {animal.name}")

    # --- Sample Users ---
    users_data = [
        {
            'username': 'daniel_m',
            'email': 'daniel@example.com',
            'password': 'testpass123',
            'currency': 5000,
            'streak': 25,
        },
        {
            'username': 'sofia_d',
            'email': 'sofia@example.com',
            'password': 'testpass123',
            'currency': 1500,
            'streak': 7,
        },
        {
            'username': 'carl_j',
            'email': 'carl@example.com',
            'password': 'testpass123',
            'currency': 800,
            'streak': 3,
        },
    ]

    for u_data in users_data:
        user, created = User.objects.get_or_create(
            username=u_data['username'],
            defaults={'email': u_data['email']}
        )
        if created:
            user.set_password(u_data['password'])
            user.save()

        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'currency': u_data['currency'],
                'streak': u_data['streak'],
                'last_study_date': timezone.now().date(),
            }
        )
        print(f"  {'Created' if created else 'Found'} user: {user.username}")

        # Give Daniel some animals
        if u_data['username'] == 'daniel_m':
            for animal_name in ['Camel', 'Fox', 'Penguin']:
                UserZoo.objects.get_or_create(user=user, animal=animals[animal_name])

        # Give Sofia one animal
        if u_data['username'] == 'sofia_d':
            UserZoo.objects.get_or_create(user=user, animal=animals['Clownfish'])

    # --- Sample Tasks ---
    daniel = User.objects.get(username='daniel_m')

    tasks_data = [
        {'title': 'Do maths reading', 'deadline': timezone.now() + timedelta(hours=6), 'completed': True},
        {'title': 'Do Java lab', 'deadline': timezone.now() + timedelta(hours=8), 'completed': False},
        {'title': 'Write philosophy essay', 'deadline': timezone.now() + timedelta(days=3), 'completed': False},
        {'title': 'Create 3 personas', 'deadline': timezone.now() + timedelta(hours=6), 'completed': False},
        {'title': 'Do maths homework', 'deadline': timezone.now() + timedelta(hours=1), 'completed': False},
    ]

    for t_data in tasks_data:
        task, created = Task.objects.get_or_create(
            user=daniel,
            title=t_data['title'],
            defaults={
                'deadline': t_data['deadline'],
                'completed': t_data['completed'],
            }
        )
        print(f"  {'Created' if created else 'Found'} task: {task.title}")

    # --- Sample Study Sessions ---
    for i in range(5):
        StudySession.objects.get_or_create(
            user=daniel,
            duration_minutes=(i + 1) * 30,
            date=timezone.now().date() - timedelta(days=i),
        )

    print("\nPopulation complete!")


if __name__ == '__main__':
    print("Starting ZooStudy population script...")
    populate()
