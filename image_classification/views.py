from django.contrib import messages
from .models import Upload, Profile
from .predictor import predict_celebrity
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm, LoginForm, UploadForm
from django.contrib.auth.models import User

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

def guest_upload(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)

            # Handle guest upload (no profile associated)
            if 'profile_id' not in request.session:
                upload.user = None  # For guest users, leave user as None
            else:
                profile = Profile.objects.get(id=request.session['profile_id'])
                upload.user = profile  # Assign the profile if logged in

            # Predict the celebrity from the uploaded image
            result = predict_celebrity(request.FILES['image'])

            # Save the prediction in the database
            upload.predicted_celebrity = result['celebrity']
            upload.confidence = result['confidence']
            upload.save()

            # Pass the result to the success page (for guest)
            return render(request, 'upload_success.html', {'result': result, 'guest': True})
    else:
        form = UploadForm()

    return render(request, 'upload.html', {'form': form, 'guest': True})  # Mark as guest upload

@login_required
def upload_image(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            # For authenticated users, get the profile from the session
            profile = Profile.objects.get(id=request.session['profile_id'])
            upload = form.save(commit=False)
            upload.user = profile  # Assign the Profile to the upload

            # Predict the celebrity from the uploaded image
            result = predict_celebrity(request.FILES['image'])

            # Save the prediction in the database
            upload.predicted_celebrity = result['celebrity']
            upload.confidence = result['confidence']
            upload.save()

            # Pass the result to the success page
            return render(request, 'upload_success.html', {'result': result, 'guest': False})
    else:
        form = UploadForm()
    return render(request, 'upload.html', {'form': form, 'guest': False})  # Mark as authenticated upload

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
            # Create a new Profile and set the password
            profile = Profile(username=form.cleaned_data['username'])
            profile.set_password(form.cleaned_data['password'])
            profile.save()

            return redirect('login')
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
                return redirect('upload')
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
