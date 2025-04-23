# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',         views.home,           name='home'),           # ← home page
    path('upload/',  views.upload_image,   name='upload_image'),
    path('success/', views.upload_success, name='upload_success'),
]