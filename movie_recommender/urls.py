from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('home/details/<int:id>/', views.details, name = 'details'),
    path('search/', views.movie_search, name = 'movie_search')
    
]