from django.urls import path
from api import views

urlpatterns = [
    path('hattrick/login/', views.hattrick_login, name='hattrick_login'),
    path('hattrick/callback/', views.hattrick_callback, name='hattrick_callback'),
]
