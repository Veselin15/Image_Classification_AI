from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import render
from .models import Upload
from .models import Upload, Profile
from .predictor import predict_celebrity
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm, LoginForm, UploadForm
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.conf import settings

def login_required(view_func):
    """Decorator to ensure the user is logged in."""
    def wrapper(request, *args, **kwargs):
        if 'profile_id' not in request.session:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def home(request):
    profile = None
    if 'profile_id' in request.session:
        try:
            profile = Profile.objects.get(id=request.session['profile_id'])
        except Profile.DoesNotExist:
            pass
    return render(request, 'home.html', {'profile': profile})

from django.core.files.storage import FileSystemStorage

def guest_upload(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = request.FILES['image']

            # Save image temporarily using FileSystemStorage
            fs = FileSystemStorage()
            filename = fs.save(f'temp/{image_file.name}', image_file)
            image_url = fs.url(filename)  # Get the URL to access the file

            # Predict the celebrity
            result = predict_celebrity(image_file)

            # Pass the result, image URL, and guest status to the success page
            return render(request, 'upload_success.html', {
                'result': result,
                'guest': 'profile_id' not in request.session,  # True if guest, False if logged in
                'image_url': image_url
            })
    else:
        form = UploadForm()

    return render(request, 'upload.html', {'form': form})


def upload_image(request):
    profile = Profile.objects.get(id=request.session['profile_id'])  # Get profile from session

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.user = profile  # Assign the Profile to the upload

            # Predict the celebrity from the uploaded image
            result = predict_celebrity(request.FILES['image'])

            # Save the prediction in the database
            upload.predicted_celebrity = result['celebrity']
            upload.confidence = result['confidence']
            upload.save()

            # Pass the result to the success page
            return render(request, 'upload_success.html', {'result': result, 'guest': False, 'image_url': upload.image.url})
    else:
        form = UploadForm()

    return render(request, 'upload.html', {'form': form, 'guest': False, 'profile': profile})  # Pass profile
@login_required
def upload_success(request):
    profile_id = request.session.get('profile_id')
    if profile_id:
        profile = Profile.objects.get(id=profile_id)
        latest_upload = Upload.objects.filter(user=profile).last()
        return render(request, 'upload_success.html', {'result': latest_upload, 'guest': False})
    else:
        return redirect('login')

# Register
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                profile = Profile(username=form.cleaned_data['username'])
                profile.set_password(form.cleaned_data['password'])
                profile.save()
                return redirect('login')
            except IntegrityError:
                messages.error(request, "Username already exists.")
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

# Login
def user_login(request):
    form = LoginForm()
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            profile = Profile.objects.get(username=username)
            if profile.check_password(password):
                # Create a session for the user
                request.session['profile_id'] = profile.id  # Store profile ID in session
                return redirect('home')
            else:
                messages.error(request, "Invalid password")
        except Profile.DoesNotExist:
            messages.error(request, "Username does not exist")

    return render(request, 'login.html', {'form': form})

# Logout
def user_logout(request):
    # Clear the session
    request.session.flush()
    return redirect('home')



def upload_list(request):
    uploads = Upload.objects.all().order_by('-confidence')  # Highest confidence first
    return render(request, 'upload_list.html', {'uploads': uploads})
