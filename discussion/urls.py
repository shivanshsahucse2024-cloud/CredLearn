from django.urls import path
from . import views

app_name = 'discussion'

urlpatterns = [
    path('', views.ThreadListView.as_view(), name='thread_list'),
    path('create/', views.ThreadCreateView.as_view(), name='thread_create'),
    path('<int:pk>/', views.ThreadDetailView.as_view(), name='thread_detail'),
    path('<int:thread_id>/comment/', views.CommentCreateView.as_view(), name='comment_create'),
    path('vote/', views.VoteView.as_view(), name='vote'),
    path('report/', views.ReportView.as_view(), name='report'),
]
