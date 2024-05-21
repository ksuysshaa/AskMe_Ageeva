from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<str:tag_name>/', views.by_tag, name='tag'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('login/', views.log_in, name='login'),
    path('signup/', views.signup, name='signup'),
    path('ask/', views.ask, name='ask'),
    path('profile/edit', views.settings, name='settings'),
    path('end_session', views.end_session, name='end_session'),
]