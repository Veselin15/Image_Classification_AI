# urls.py
from django.urls import path
from . import views

# Note: The settings and static imports are not needed here
# as they are handled in the project-level urls.py

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_image, name='upload_image'), # Renamed for clarity
    path('guest/upload/', views.guest_upload, name='guest_upload'),
    # The 'upload_success' path is removed as it's no longer a separate view
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    # The 'upload_list' path is removed as the view does not exist
]