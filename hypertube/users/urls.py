from django.urls import path, include
from django.conf.urls import url
from . import views
from django.views.static import serve 
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('list_user/', views.list_user, name='list_user'),
    path('profile/', views.profile, name='profile'),
    path('public_profile/', views.public_profile_redirect, name='public_profile_redirect'),
    path('public_profile/<int:id_user>/', views.public_profile, name='public_profile'),
    url('^', include('django.contrib.auth.urls')),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate')
]
