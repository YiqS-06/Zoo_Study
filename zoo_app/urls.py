from django.urls import path
from zoo_app import views

app_name = 'zoo_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('zoo/', views.zoo, name='zoo'),
    path('zoo/shop/', views.shop, name='shop'),
    path('study/', views.study_hub, name='study_hub'),
    path('study/notes/', views.notes, name='notes'),
    # AJAX endpoints
    path('ajax/buy-animal/', views.buy_animal, name='buy_animal'),
    path('ajax/log-session/', views.log_study_session, name='log_study_session'),
    path('ajax/toggle-task/', views.toggle_task_complete, name='toggle_task_complete'),
]
