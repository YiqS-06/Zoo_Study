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
]
