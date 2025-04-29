# urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('',         views.home,           name='home'),
    path('upload/',  views.upload_image,   name='upload'),
    path('guest/upload/', views.guest_upload, name='guest_upload'),
    path('success/', views.upload_success, name='upload_success'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('upload_list/', views.upload_list, name='upload_list'),
]