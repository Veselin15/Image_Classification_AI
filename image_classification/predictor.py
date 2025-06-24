# recognition/predictor.py

import os
from PIL import Image
from django.conf import settings

# --- Lazy-loaded global variables for models AND modules ---
# We will initialize everything to None and load them on the first request.
svm = None
scaler = None
class_dict = None
mtcnn = None
resnet = None
device = None
torch = None
np = None
joblib = None
MTCNN = None
InceptionResnetV1 = None


def _initialize_models():
    """
    Loads and initializes all libraries and models.
    This function is called only once on the first prediction request.
    """
    # Make all globals modifiable
    global svm, scaler, class_dict, mtcnn, resnet, device
    global torch, np, joblib, MTCNN, InceptionResnetV1

    # Check if already initialized to prevent reloading
    if svm is not None:
        return

    print("INFO: Lazily importing heavy libraries and initializing models...")

    # --- Import heavy libraries here, inside the function ---
    import torch as torch_local
    import numpy as np_local
    import joblib as joblib_local
    from facenet_pytorch import MTCNN as MTCNN_local, InceptionResnetV1 as InceptionResnetV1_local

    # Assign the imported modules to our global variables
    torch = torch_local
    np = np_local
    joblib = joblib_local
    MTCNN = MTCNN_local
    InceptionResnetV1 = InceptionResnetV1_local

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
    # This call will ensure all modules and models are loaded.
    _initialize_models()

    try:
        img = Image.open(image_path).convert('RGB')
    except Exception as e:
        # Use a dictionary for a consistent return format
        return {"error": f"Error opening image: {e}"}

    # Detect face
    face = mtcnn(img)
    if face is None:
        return {"error": "No face detected"}

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

    return {
        "celebrity": predicted_class_name,
        "confidence": float(confidence)
    }