from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('create-course/', views.create_course, name='create_course'),
    path('join/<int:course_id>/', views.join_course, name='join_course'),
]