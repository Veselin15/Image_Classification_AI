from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib import messages
from .forms import UploadForm, RegisterForm, LoginForm
# We REMOVE the predictor import from here
from .models import Upload, Profile


def home(request):
    return render(request, 'home.html')


def guest_upload(request):
    # We IMPORT the predictor function HERE, only when needed.
    from .predictor import predict_celebrity

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = request.FILES['image']

            result = predict_celebrity(image_file)

            if "error" in result:
                messages.error(request, result["error"])
                return render(request, 'guest_upload.html', {'form': form})

            upload = Upload.objects.create(
                image=image_file,
                predicted_celebrity=result.get('celebrity', 'N/A'),
                confidence=result.get('confidence', 0.0)
            )

            return render(request, 'upload_success.html', {'result': upload, 'guest': True})
    else:
        form = UploadForm()
    return render(request, 'guest_upload.html', {'form': form})


@login_required
def upload_image(request):
    # We also IMPORT the predictor function HERE.
    from .predictor import predict_celebrity

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.user = request.user

            result = predict_celebrity(request.FILES['image'])

            if "error" in result:
                messages.error(request, result["error"])
                return render(request, 'upload.html', {'form': form})

            upload.predicted_celebrity = result.get('celebrity', 'N/A')
            upload.confidence = result.get('confidence', 0.0)
            upload.save()

            return render(request, 'upload_success.html', {'result': upload, 'guest': False})
    else:
        form = UploadForm()
    return render(request, 'upload.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                user = User.objects.create_user(username=username, password=password)
                Profile.objects.create(user=user)
                messages.success(request, 'Registration successful! Please log in.')
                return redirect('login')
            except IntegrityError:
                messages.error(request, 'Username already exists.')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('upload_image')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    return redirect('home')