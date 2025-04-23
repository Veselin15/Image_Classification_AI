# views.py
from django.shortcuts import render, redirect
from .forms import UploadForm
from .models import Upload
from django.contrib.auth.decorators import login_required
from .predictor import predict_celebrity


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
