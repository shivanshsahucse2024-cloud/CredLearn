from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('wallet/', views.wallet, name='wallet'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('create-course/', views.create_course, name='create_course'),
    path('join/<int:course_id>/', views.join_course, name='join_course'),
    path('book/<int:slot_id>/', views.book_slot, name='book_slot'),
    path('course/edit/<int:course_id>/', views.edit_course, name='edit_course'),
    path('course/delete/<int:course_id>/', views.delete_course, name='delete_course'),
    
    # Discovery
    path('explore/', views.category_list, name='category_list'),
    path('category/<int:category_id>/', views.course_list_by_category, name='course_list_by_category'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),

    # Expanded Dashboards
    path('learning/', views.my_learning, name='my_learning'),
    path('teaching/', views.my_teaching, name='my_teaching'),
    path('course/learn/<int:course_id>/', views.course_dashboard_student, name='course_dashboard_student'),
    path('course/teach/<int:course_id>/', views.course_dashboard_teacher, name='course_dashboard_teacher'),
    path('u/<str:username>/', views.public_profile, name='public_profile'),
]