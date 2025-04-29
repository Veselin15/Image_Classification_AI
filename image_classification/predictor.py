# recognition/predictor.py

import os
import joblib
import numpy as np
import torch
from PIL import Image
from django.conf import settings
from facenet_pytorch import MTCNN, InceptionResnetV1

# ── Load your SVM+scaler+classes once at import ──
MODEL_PATH = os.path.join(settings.BASE_DIR, 'model', 'facenet_svm_extended.pkl')
# print(f"DEBUG ▶️ Loading model from: {MODEL_PATH}")
model_data = joblib.load(MODEL_PATH)
svm         = model_data['svm']
scaler      = model_data['scaler']
class_dict  = model_data['class_dict']

# ── Init Face detector & FaceNet once ──
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
mtcnn  = MTCNN(
    image_size=160,
    margin=20,         # more padding around the detected face
    min_face_size=10,  # detect smaller faces
    keep_all=False,
    device=device
)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)


def predict_celebrity(file_obj):
    """
    file_obj can be an InMemoryUploadedFile or a path-like; PIL.Image.open handles both.
    Returns dict: { 'celebrity': str, 'confidence': float }
    """
    # 1️⃣ Load + inspect image
    img = Image.open(file_obj).convert('RGB')
    # print("DEBUG ▶️ Input image size:", img.size)

    # 2️⃣ Face detection
    face_tensor = mtcnn(img)
    # print("DEBUG ▶️ face_tensor:", face_tensor)
    if face_tensor is None:
        # print("DEBUG ▶️ No face detected — returning Unknown")
        return {'celebrity': 'Unknown', 'confidence': 0.0}

    # 3️⃣ Compute embedding
    with torch.no_grad():
        emb = resnet(face_tensor.unsqueeze(0).to(device)).cpu().numpy().flatten()
    # print("DEBUG ▶️ Embedding vector shape:", emb.shape)

    # 4️⃣ Scale + predict
    emb_scaled = scaler.transform([emb])
    probs      = svm.predict_proba(emb_scaled)[0]
    top_idx    = int(np.argmax(probs))
    name       = [k for k, v in class_dict.items() if v == top_idx][0]
    confidence = probs[top_idx] * 100
    # print(f"DEBUG ▶️ Prediction: {name} @ {confidence:.2f}%")

    # 5️⃣ Return result
    return {'celebrity': name, 'confidence': round(confidence, 2)}
