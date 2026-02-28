from django.contrib import admin
from zoo_app.models import UserProfile, Task, StudySession, Animal, UserZoo, Resource


admin.site.register(UserProfile)
admin.site.register(Task)
admin.site.register(StudySession)
admin.site.register(Animal)
admin.site.register(UserZoo)
admin.site.register(Resource)
