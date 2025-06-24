# recognition/predictor.py

import os
import joblib
import numpy as np
import torch
from PIL import Image
from django.conf import settings
from facenet_pytorch import MTCNN, InceptionResnetV1

# --- Lazy-loaded global variables ---
# We will initialize these to None and load them on the first request.
svm = None
scaler = None
class_dict = None
mtcnn = None
resnet = None
device = None


def _initialize_models():
    """
    Loads and initializes all models and data.
    This function is called only once on the first prediction request.
    """
    global svm, scaler, class_dict, mtcnn, resnet, device

    # Check if already initialized to prevent reloading
    if svm is not None:
        return

    print("INFO: Initializing models for the first time...")

    # ── Load your SVM+scaler+classes ──
    MODEL_PATH = os.path.join(settings.BASE_DIR, 'model', 'facenet_svm_extended.pkl')
    model_data = joblib.load(MODEL_PATH)
    svm = model_data['svm']
    scaler = model_data['scaler']
    class_dict = model_data['class_dict']

    # ── Init Face detector & FaceNet ──
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    mtcnn = MTCNN(
        image_size=160,
        margin=20,
        min_face_size=10,
        keep_all=False,
        device=device
    )
    resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)
    print("INFO: Models initialized successfully.")


def predict_celebrity(image_path):
    """
    Predicts the celebrity in a given image.
    """
    # Ensure models are loaded before proceeding
    _initialize_models()

    try:
        img = Image.open(image_path).convert('RGB')
    except Exception as e:
        return f"Error opening image: {e}", None

    # Detect face
    face = mtcnn(img)
    if face is None:
        return "No face detected", None

    # Generate embedding
    with torch.no_grad():
        embedding = resnet(face.unsqueeze(0).to(device))

    # Scale embedding and predict
    embedding_scaled = scaler.transform(embedding.cpu().numpy())
    prediction_proba = svm.predict_proba(embedding_scaled)[0]

    # Get the top prediction
    max_proba_idx = np.argmax(prediction_proba)
    confidence = prediction_proba[max_proba_idx]

    # Use the class dictionary to get the name
    predicted_class_name = class_dict.get(max_proba_idx, "Unknown")

    return predicted_class_name, confidence