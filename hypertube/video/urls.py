from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.list, name='list'),
    path('video/<slug:tittle>/', views.video, name='tittle_video'),
    path('video/<slug:title>/<slug:season>/<slug:episode>/', views.watch_serie, name='watch_serie'),
    path('video/serie/<slug:title>/', views.serie, name='serie'),
    path('', views.filtre, name='list'),
    path('search/', views.search, name='search'),
]
