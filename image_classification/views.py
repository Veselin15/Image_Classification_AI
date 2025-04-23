# views.py
from django.contrib import messages

from .models import Upload
from .predictor import predict_celebrity
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm, UploadForm
from django.contrib.auth.models import User

def home(request):
    return render(request, 'home.html')

@login_required
def upload_image(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.user = request.user

            # Predict the celebrity from the uploaded image
            result = predict_celebrity(request.FILES['image'])

            # Save the prediction in the database
            upload.predicted_celebrity = result['celebrity']
            upload.confidence = result['confidence']
            upload.save()

            # Pass the result to the success page
            return render(request, 'upload_success.html', {'result': result})

    else:
        form = UploadForm()
    return render(request, 'upload.html', {'form': form})


# Add this new view for 'upload_success'
@login_required
def upload_success(request):
    # Here, you can pass the prediction results to the template
    # Optionally, retrieve the latest uploaded image and its result
    latest_upload = Upload.objects.filter(user=request.user).last()
    return render(request, 'upload_success.html', {'upload': latest_upload})

# Register
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash the password
            user.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

# Login
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('upload')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

# Logout
def user_logout(request):
    print("Logout view reached.")
    logout(request)
    request.session.flush()
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')
