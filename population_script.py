import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zoo_study.settings')

import django
django.setup()

from django.contrib.auth.models import User
from zoo_app.models import UserProfile, Task, StudySession, Animal, UserZoo, Resource
from datetime import timedelta
from django.utils import timezone


def add_animals():
    """Create 12 animals across 4 habitat categories (3 each).
    Costs range from 2000 to 10000 coins, scaling with rarity.
    """
    animals_data = [
        # Desert animals (cheapest tier)
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
        # Polar animals (most expensive tier)
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

    return animals


def add_users():
    """Create 3 sample users matching our Design Spec personas.
    Each has different currency, streak, and progress levels.
    """
    users_data = [
        {
            'username': 'daniel_m',
            'email': 'daniel@example.com',
            'password': 'testpass123',
            'currency': 5000,
            'streak': 25,
            'last_study_date': timezone.now().date(),
        },
        {
            'username': 'sofia_d',
            'email': 'sofia@example.com',
            'password': 'testpass123',
            'currency': 1500,
            'streak': 7,
            'last_study_date': timezone.now().date(),
        },
        {
            'username': 'carl_j',
            'email': 'carl@example.com',
            'password': 'testpass123',
            'currency': 800,
            'streak': 3,
            'last_study_date': timezone.now().date() - timedelta(days=2),
        },
    ]

    users = {}
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
                'last_study_date': u_data['last_study_date'],
            }
        )
        users[u_data['username']] = user
        print(f"  {'Created' if created else 'Found'} user: {user.username}")

    return users


def add_zoo_entries(users, animals):
    """Assign owned animals to users.
    Daniel (power user) has 3, Sofia has 1, Carl has none yet.
    """
    zoo_data = {
        'daniel_m': ['Camel', 'Fox', 'Penguin'],
        'sofia_d': ['Clownfish'],
    }

    for username, animal_names in zoo_data.items():
        user = users[username]
        for name in animal_names:
            _, created = UserZoo.objects.get_or_create(
                user=user, animal=animals[name]
            )
            if created:
                print(f"  {username} acquired {name}")


def add_tasks(users):
    """Create sample tasks for all users with varying deadlines and statuses.
    Returns dict of tasks for linking Resources later.
    """
    now = timezone.now()

    tasks_data = {
        'daniel_m': [
            {'title': 'Do maths reading', 'deadline': now + timedelta(hours=6), 'completed': True},
            {'title': 'Do Java lab', 'deadline': now + timedelta(hours=8), 'completed': False},
            {'title': 'Write philosophy essay', 'deadline': now + timedelta(days=3), 'completed': False},
            {'title': 'Create 3 personas', 'deadline': now + timedelta(hours=6), 'completed': False},
            {'title': 'Do maths homework', 'deadline': now + timedelta(hours=1), 'completed': False},
        ],
        'sofia_d': [
            {'title': 'Business case study', 'deadline': now + timedelta(days=2), 'completed': False},
            {'title': 'Accounting worksheet', 'deadline': now + timedelta(hours=12), 'completed': True},
            {'title': 'Marketing presentation', 'deadline': now + timedelta(days=5), 'completed': False},
        ],
        'carl_j': [
            {'title': 'Algorithms coursework', 'deadline': now + timedelta(days=4), 'completed': False},
            {'title': 'Database lab exercises', 'deadline': now - timedelta(hours=2), 'completed': False},
            {'title': 'Networking quiz prep', 'deadline': now + timedelta(days=1), 'completed': False},
        ],
    }

    all_tasks = {}
    for username, task_list in tasks_data.items():
        user = users[username]
        all_tasks[username] = []
        for t_data in task_list:
            task, created = Task.objects.get_or_create(
                user=user,
                title=t_data['title'],
                defaults={
                    'deadline': t_data['deadline'],
                    'completed': t_data['completed'],
                }
            )
            all_tasks[username].append(task)
            print(f"  {'Created' if created else 'Found'} task: {task.title} ({username})")

    return all_tasks


def add_study_sessions(users):
    """Create study session history for all users.
    Daniel has consistent daily sessions, Sofia has a few,
    Carl has sporadic short sessions.
    """
    sessions_data = {
        'daniel_m': [
            (120, 0), (90, 1), (60, 2), (150, 3), (45, 4),
            (80, 5), (110, 6), (30, 7),
        ],
        'sofia_d': [
            (60, 0), (45, 1), (30, 3), (90, 5),
        ],
        'carl_j': [
            (20, 0), (15, 2), (10, 5),
        ],
    }

    for username, sessions in sessions_data.items():
        user = users[username]
        for duration, days_ago in sessions:
            _, created = StudySession.objects.get_or_create(
                user=user,
                duration_minutes=duration,
                date=timezone.now().date() - timedelta(days=days_ago),
            )
            if created:
                print(f"  {username}: {duration} min ({days_ago} days ago)")


def add_resources(all_tasks):
    """Create sample notes and resources linked to tasks.
    Demonstrates both types: notes (user-written content) and
    resources (external links).
    """
    resources_data = {
        'daniel_m': [
            # Resources for 'Do maths reading'
            {'task_index': 0, 'title': 'Chapter 5 Notes', 'type': 'note',
             'content': 'Key concepts: integration by parts, substitution method. Remember to practise examples 5.3 and 5.7.'},
            {'task_index': 0, 'title': 'Khan Academy - Integration', 'type': 'resource',
             'url': 'https://www.khanacademy.org/math/calculus-1'},
            # Resources for 'Do Java lab'
            {'task_index': 1, 'title': 'Lab 4 Instructions', 'type': 'note',
             'content': 'Implement a linked list with add, remove, and search. Use generics for type safety.'},
            {'task_index': 1, 'title': 'Java Docs - LinkedList', 'type': 'resource',
             'url': 'https://docs.oracle.com/javase/8/docs/api/java/util/LinkedList.html'},
            # Resources for 'Write philosophy essay'
            {'task_index': 2, 'title': 'Essay Outline', 'type': 'note',
             'content': 'Thesis: Kant\'s categorical imperative is incompatible with utilitarian ethics.\n\n1. Intro - define both frameworks\n2. Key differences\n3. Case study analysis\n4. Conclusion'},
            {'task_index': 2, 'title': 'Stanford Encyclopedia - Kant', 'type': 'resource',
             'url': 'https://plato.stanford.edu/entries/kant-moral/'},
        ],
        'sofia_d': [
            # Resources for 'Business case study'
            {'task_index': 0, 'title': 'Case Study Notes', 'type': 'note',
             'content': 'Analyse Tesla\'s market entry strategy. Focus on: first-mover advantage, vertical integration, brand positioning.'},
            {'task_index': 0, 'title': 'Harvard Business Review', 'type': 'resource',
             'url': 'https://hbr.org/'},
            # Resources for 'Marketing presentation'
            {'task_index': 2, 'title': 'Slide Ideas', 'type': 'note',
             'content': 'Cover: target audience, marketing mix (4Ps), social media strategy, budget breakdown. Keep it under 10 slides.'},
        ],
        'carl_j': [
            # Resources for 'Algorithms coursework'
            {'task_index': 0, 'title': 'Sorting Algorithms Summary', 'type': 'note',
             'content': 'Quick sort: O(n log n) avg, O(n^2) worst. Merge sort: O(n log n) always but uses O(n) space. Heap sort: O(n log n) in-place.'},
            {'task_index': 0, 'title': 'GeeksForGeeks - Sorting', 'type': 'resource',
             'url': 'https://www.geeksforgeeks.org/sorting-algorithms/'},
            # Resources for 'Database lab exercises'
            {'task_index': 1, 'title': 'W3Schools - SQL Joins', 'type': 'resource',
             'url': 'https://www.w3schools.com/sql/sql_join.asp'},
        ],
    }

    for username, res_list in resources_data.items():
        for r_data in res_list:
            task = all_tasks[username][r_data['task_index']]
            resource, created = Resource.objects.get_or_create(
                task=task,
                title=r_data['title'],
                defaults={
                    'type': r_data['type'],
                    'content': r_data.get('content', ''),
                    'url': r_data.get('url', ''),
                }
            )
            print(f"  {'Created' if created else 'Found'} {r_data['type']}: {resource.title}")


def populate():
    print("--- Adding Animals ---")
    animals = add_animals()

    print("\n--- Adding Users ---")
    users = add_users()

    print("\n--- Adding Zoo Entries ---")
    add_zoo_entries(users, animals)

    print("\n--- Adding Tasks ---")
    all_tasks = add_tasks(users)

    print("\n--- Adding Study Sessions ---")
    add_study_sessions(users)

    print("\n--- Adding Notes & Resources ---")
    add_resources(all_tasks)

    # Print summary
    print("\n" + "=" * 40)
    print("Population Summary:")
    print(f"  Animals:        {Animal.objects.count()}")
    print(f"  Users:          {User.objects.count()}")
    print(f"  Zoo entries:    {UserZoo.objects.count()}")
    print(f"  Tasks:          {Task.objects.count()}")
    print(f"  Study sessions: {StudySession.objects.count()}")
    print(f"  Resources:      {Resource.objects.count()}")
    print("=" * 40)
    print("Population complete!")


if __name__ == '__main__':
    print("Starting ZooStudy population script...\n")
    populate()