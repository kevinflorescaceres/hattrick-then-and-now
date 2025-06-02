from django.urls import path
from api import views
from api.views import get_players

urlpatterns = [
    path('hattrick/login/', views.hattrick_login, name='hattrick_login'),
    path('hattrick/callback/', views.hattrick_callback, name='hattrick_callback'),
    path('hattrick/test/', views.hattrick_test_endpoint, name='hattrick_test_endpoint'),
    path('hattrick/players/', get_players, name='get_players'),
]
