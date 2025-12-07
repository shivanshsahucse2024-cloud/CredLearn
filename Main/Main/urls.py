"""
URL configuration for Main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from Home import views
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView   


admin.site.site_header = "Shivansh Admin"
admin.site.site_title = "Shivansh Admin Portal"
admin.site.index_title = "Welcome to Shivansh Researcher Portal"

urlpatterns = [
    path('admin/',admin.site.urls),
    path('',views.home,name='home'),
    path('explore/',views.Explore,name='explore'),
    path('about/',views.about,name='about'),
    path('contact/',views.contact,name='contact'),
    path('services/',views.services,name='services'),
    path('programming/',views.programming,name='programming'),
    path('Design/',views.Design,name='Design'),
    path('Music/',views.Music,name='Music'),
    path('Lang/',views.Lang,name='Lang'),
    path('cooking/',views.cooking,name='cooking'),
    path('business/',views.business,name='business'),
    path('dancing/',views.dancing,name='dancing'),
    #path('login/',views.login,name='login'),
    path('register/',views.register,name='register'),
    path('mentor/',views.mentor,name='mentor'),
     # Wallet
    path('wallet/', views.wallet, name='wallet'),
    
    # Live Session
    path('host-session/', views.host_session, name='host_session'),
    path('join-session/<int:session_id>/', views.join_session, name='join_session'),
    path("sessions/", views.session_list, name="session_list"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),

   #path('logout/', LogoutView.as_view(next_page='/login/', http_method_names=['get']), name='logout'),
   path('logout/', views.logout_user, name='logout'),
   path('browse-sessions/', views.browse_sessions, name='browse_sessions'),

]  