# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',         views.home,           name='home'),
    path('upload/',  views.upload_image,   name='upload'),
    path('guest/upload/', views.guest_upload, name='guest_upload'),
    path('success/', views.upload_success, name='upload_success'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]