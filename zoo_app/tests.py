from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from zoo_app.models import UserProfile, Task, StudySession, Animal, UserZoo, Resource


# ======== MODEL TESTS ========

class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass1234')
        self.profile = UserProfile.objects.create(user=self.user)

    def test_profile_created(self):
        self.assertEqual(str(self.profile), 'testuser')
        self.assertEqual(self.profile.currency, 0)
        self.assertEqual(self.profile.streak, 0)

    def test_add_currency(self):
        earned = self.profile.add_currency(10)
        self.assertEqual(earned, 100)
        self.assertEqual(self.profile.currency, 100)

    def test_update_streak_first_session(self):
        self.profile.update_streak()
        self.assertEqual(self.profile.streak, 1)

    def test_update_streak_same_day(self):
        self.profile.update_streak()
        self.profile.update_streak()  # Same day again
        self.assertEqual(self.profile.streak, 1)

    def test_update_streak_consecutive(self):
        self.profile.last_study_date = timezone.now().date() - timedelta(days=1)
        self.profile.streak = 3
        self.profile.save()
        self.profile.update_streak()
        self.assertEqual(self.profile.streak, 4)

    def test_update_streak_broken(self):
        self.profile.last_study_date = timezone.now().date() - timedelta(days=3)
        self.profile.streak = 5
        self.profile.save()
        self.profile.update_streak()
        self.assertEqual(self.profile.streak, 1)

    def test_total_study_minutes_no_sessions(self):
        self.assertEqual(self.profile.total_study_minutes(), 0)

    def test_total_study_minutes_with_sessions(self):
        StudySession.objects.create(user=self.user, duration_minutes=30)
        StudySession.objects.create(user=self.user, duration_minutes=45)
        self.assertEqual(self.profile.total_study_minutes(), 75)

    def test_zoo_animal_count(self):
        self.assertEqual(self.profile.zoo_animal_count(), 0)
        animal = Animal.objects.create(name='Lion', slug='lion', category='forest', cost=100)
        UserZoo.objects.create(user=self.user, animal=animal)
        self.assertEqual(self.profile.zoo_animal_count(), 1)


class AnimalModelTest(TestCase):
    def test_animal_creation(self):
        animal = Animal.objects.create(name='Penguin', slug='penguin', category='polar', cost=300)
        self.assertEqual(str(animal), 'Penguin')
        self.assertEqual(animal.slug, 'penguin')

    def test_study_hours_required(self):
        # cost=300, COINS_PER_MINUTE=10 → 30 mins → 0.5 hours
        animal = Animal.objects.create(name='Seal', slug='seal', category='polar', cost=300)
        self.assertEqual(animal.study_hours_required, 0.5)

    def test_slug_auto_generated_on_save(self):
        animal = Animal(name='Snow Leopard', category='polar', cost=500)
        animal.save()
        self.assertEqual(animal.slug, 'snow-leopard')


class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='taskuser', password='pass1234')

    def test_task_creation(self):
        task = Task.objects.create(
            user=self.user,
            title='Write essay',
            deadline=timezone.now() + timedelta(days=2)
        )
        self.assertEqual(str(task), 'Write essay')
        self.assertFalse(task.completed)
        self.assertFalse(task.is_overdue)

    def test_task_overdue(self):
        task = Task.objects.create(
            user=self.user,
            title='Old task',
            deadline=timezone.now() - timedelta(days=1)
        )
        self.assertTrue(task.is_overdue)

    def test_time_remaining_display_overdue(self):
        task = Task.objects.create(
            user=self.user,
            title='Past task',
            deadline=timezone.now() - timedelta(hours=1)
        )
        self.assertEqual(task.time_remaining_display, 'Overdue')


class StudySessionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='studyuser', password='pass1234')
        UserProfile.objects.create(user=self.user)

    def test_log_session_valid(self):
        session, coins = StudySession.log_session(self.user, 30)
        self.assertIsNotNone(session)
        self.assertEqual(coins, 300)
        self.assertEqual(self.user.userprofile.currency, 300)

    def test_log_session_zero_duration(self):
        session, coins = StudySession.log_session(self.user, 0)
        self.assertIsNone(session)
        self.assertEqual(coins, 0)

    def test_coins_earned_property(self):
        session = StudySession.objects.create(user=self.user, duration_minutes=5)
        self.assertEqual(session.coins_earned, 50)

    def test_duration_display(self):
        session = StudySession.objects.create(user=self.user, duration_minutes=90)
        self.assertEqual(session.duration_display, '1h 30m')


class BuyAnimalTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='buyer', password='pass1234')
        self.profile = UserProfile.objects.create(user=self.user, currency=500)
        self.animal = Animal.objects.create(name='Fox', slug='fox', category='forest', cost=300)

    def test_buy_success(self):
        success, msg = self.profile.buy_animal(self.animal)
        self.assertTrue(success)
        self.assertEqual(self.profile.currency, 200)
        self.assertTrue(UserZoo.objects.filter(user=self.user, animal=self.animal).exists())

    def test_buy_insufficient_funds(self):
        self.profile.currency = 100
        self.profile.save()
        success, msg = self.profile.buy_animal(self.animal)
        self.assertFalse(success)
        self.assertIn('200', msg)

    def test_buy_duplicate(self):
        self.profile.currency = 1000
        self.profile.save()
        self.profile.buy_animal(self.animal)
        success, msg = self.profile.buy_animal(self.animal)
        self.assertFalse(success)
        self.assertIn('already own', msg)


# ======== VIEW TESTS ========

class PublicViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_returns_200(self):
        response = self.client.get(reverse('zoo_app:home'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_get(self):
        response = self.client.get(reverse('zoo_app:login'))
        self.assertEqual(response.status_code, 200)

    def test_register_page_get(self):
        response = self.client.get(reverse('zoo_app:register'))
        self.assertEqual(response.status_code, 200)


class AuthRedirectTest(TestCase):
    """Unauthenticated users should be redirected to login."""
    def setUp(self):
        self.client = Client()

    def test_dashboard_redirects(self):
        response = self.client.get(reverse('zoo_app:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response['Location'])

    def test_zoo_redirects(self):
        response = self.client.get(reverse('zoo_app:zoo'))
        self.assertEqual(response.status_code, 302)

    def test_shop_redirects(self):
        response = self.client.get(reverse('zoo_app:shop'))
        self.assertEqual(response.status_code, 302)

    def test_study_hub_redirects(self):
        response = self.client.get(reverse('zoo_app:study_hub'))
        self.assertEqual(response.status_code, 302)

    def test_notes_redirects(self):
        response = self.client.get(reverse('zoo_app:notes'))
        self.assertEqual(response.status_code, 302)


class RegistrationFlowTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_creates_user_and_profile(self):
        response = self.client.post(reverse('zoo_app:register'), {
            'username': 'newzookeeper',
            'email': 'zoo@test.com',
            'password': 'securePass99',
            'confirm_password': 'securePass99',
        })
        # Should redirect to dashboard after successful registration
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('zoo_app:dashboard'))
        self.assertTrue(User.objects.filter(username='newzookeeper').exists())
        user = User.objects.get(username='newzookeeper')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_register_password_mismatch(self):
        response = self.client.post(reverse('zoo_app:register'), {
            'username': 'baduser',
            'email': 'bad@test.com',
            'password': 'pass1234',
            'confirm_password': 'different',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='baduser').exists())

    def test_register_duplicate_username(self):
        User.objects.create_user(username='existing', password='pass1234')
        response = self.client.post(reverse('zoo_app:register'), {
            'username': 'existing',
            'email': 'x@test.com',
            'password': 'pass1234',
            'confirm_password': 'pass1234',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username='existing').count(), 1)


class LoginFlowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='loginuser', password='correctPass99')
        UserProfile.objects.create(user=self.user)

    def test_login_success(self):
        response = self.client.post(reverse('zoo_app:login'), {
            'username': 'loginuser',
            'password': 'correctPass99',
        })
        self.assertRedirects(response, reverse('zoo_app:dashboard'))

    def test_login_wrong_password(self):
        response = self.client.post(reverse('zoo_app:login'), {
            'username': 'loginuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)

    def test_logout_redirects_home(self):
        self.client.login(username='loginuser', password='correctPass99')
        response = self.client.get(reverse('zoo_app:logout'))
        self.assertRedirects(response, reverse('zoo_app:home'))


class AuthenticatedViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='authuser', password='pass1234')
        UserProfile.objects.create(user=self.user)
        self.client.login(username='authuser', password='pass1234')

    def test_dashboard_renders(self):
        response = self.client.get(reverse('zoo_app:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')

    def test_zoo_renders(self):
        response = self.client.get(reverse('zoo_app:zoo'))
        self.assertEqual(response.status_code, 200)

    def test_shop_renders(self):
        response = self.client.get(reverse('zoo_app:shop'))
        self.assertEqual(response.status_code, 200)

    def test_study_hub_renders(self):
        response = self.client.get(reverse('zoo_app:study_hub'))
        self.assertEqual(response.status_code, 200)

    def test_notes_renders(self):
        response = self.client.get(reverse('zoo_app:notes'))
        self.assertEqual(response.status_code, 200)


class AjaxEndpointTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='ajaxuser', password='pass1234')
        self.profile = UserProfile.objects.create(user=self.user, currency=1000)
        self.client.login(username='ajaxuser', password='pass1234')

    def test_log_study_session(self):
        response = self.client.post(
            reverse('zoo_app:log_study_session'),
            {'duration_minutes': 30},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['coins_earned'], 300)

    def test_buy_animal_ajax(self):
        animal = Animal.objects.create(name='Rabbit', slug='rabbit', category='forest', cost=200)
        response = self.client.post(
            reverse('zoo_app:buy_animal'),
            {'animal_id': animal.id},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['currency'], 800)

    def test_toggle_task_complete(self):
        task = Task.objects.create(
            user=self.user,
            title='Test task',
            deadline=timezone.now() + timedelta(days=1)
        )
        response = self.client.post(
            reverse('zoo_app:toggle_task_complete'),
            {'task_id': task.id},
        )
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['completed'])
        task.refresh_from_db()
        self.assertTrue(task.completed)
