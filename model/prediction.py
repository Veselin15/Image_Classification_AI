import os
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
import torch

# Configuration
model_path = 'facenet_svm.pkl'  # Path to the saved model
test_image_path = './test_images/popa.jpg'  # Path to the test image

# Device configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load the saved model, scaler, and class dict
model_data = joblib.load(model_path)
svm = model_data['svm']
scaler = model_data['scaler']
class_dict = model_data['class_dict']

# Initialize face detector and FaceNet model
mtcnn = MTCNN(image_size=160, margin=0, min_face_size=20, keep_all=False, device=device)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

# Helper to extract embedding from image path
def extract_embedding(img_path):
    img = Image.open(img_path).convert('RGB')
    face_tensor = mtcnn(img)
    if face_tensor is None:
        return None
    with torch.no_grad():
        embedding = resnet(face_tensor.unsqueeze(0).to(device))
    return embedding.cpu().numpy().flatten()

# Extract the embedding from the test image
embedding = extract_embedding(test_image_path)
if embedding is None:
    print("No face detected in the test image.")
else:
    # Scale the embedding
    embedding_scaled = scaler.transform([embedding])

    # Get prediction probabilities
    probabilities = svm.predict_proba(embedding_scaled)[0]
    top_idx = np.argmax(probabilities)
    predicted_class = [k for k, v in class_dict.items() if v == top_idx][0]
    confidence = probabilities[top_idx] * 100

    print(f"The predicted celebrity is: {predicted_class}")
    print(f"You look {confidence:.2f}% like {predicted_class}")
