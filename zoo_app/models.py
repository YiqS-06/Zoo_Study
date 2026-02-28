from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    currency = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)
    last_study_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    deadline = models.DateTimeField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class StudySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    duration_minutes = models.IntegerField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.duration_minutes} mins on {self.date}"


class Animal(models.Model):
    CATEGORY_CHOICES = [
        ('desert', 'Desert'),
        ('aquatic', 'Aquatic'),
        ('forest', 'Forest'),
        ('polar', 'Polar'),
    ]

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    cost = models.IntegerField()
    image = models.ImageField(upload_to='animals/', blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class UserZoo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='zoo_animals')
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    date_acquired = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'animal')

    def __str__(self):
        return f"{self.user.username} owns {self.animal.name}"


class Resource(models.Model):
    TYPE_CHOICES = [
        ('note', 'Note'),
        ('resource', 'Resource'),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    url = models.URLField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='note')

    def __str__(self):
        return self.title
