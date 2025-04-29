# train_facenet_svm_extended.py
import os
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import classification_report
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
import torch

# Configuration
dataset_dir = './celebs_dataset'           # Update this path to your celebrity dataset directory
model_out     = 'facenet_svm_extended.pkl' # Output model file

# Device configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Initialize face detector and FaceNet model
mtcnn = MTCNN(image_size=160, margin=0, min_face_size=20, keep_all=False, device=device)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

# Helper to extract embedding from image path
def extract_embedding(img_path):
    img = Image.open(img_path).convert('RGB')

    # Convert image to numpy array with the correct dtype
    img = np.array(img)
    if img.dtype != np.uint8:
        img = img.astype(np.uint8)  # Ensure it's uint8 type for image processing

    # Detect and crop face
    face_tensor = mtcnn(img)
    if face_tensor is None:
        return None

    # Get embedding
    with torch.no_grad():
        embedding = resnet(face_tensor.unsqueeze(0).to(device))
    return embedding.cpu().numpy().flatten()
# Build dataset X, y
X, y = [], []
class_dict = {}

# Loop through each celebrity folder
for idx, celeb in enumerate(sorted(os.listdir(dataset_dir))):
    celeb_dir = os.path.join(dataset_dir, celeb)
    if not os.path.isdir(celeb_dir):
        continue
    class_dict[celeb] = idx
    for fname in os.listdir(celeb_dir):
        if not fname.lower().endswith(('.jpg','jpeg','png')):  # You can add more image formats if needed
            continue
        path = os.path.join(celeb_dir, fname)
        emb = extract_embedding(path)
        if emb is None:
            continue
        X.append(emb)
        y.append(idx)

X = np.vstack(X)
y = np.array(y)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Scale features
scaler = StandardScaler().fit(X_train)
X_train_s = scaler.transform(X_train)
X_test_s  = scaler.transform(X_test)

# Train SVM classifier
svm = SVC(kernel='linear', C=10, gamma='scale', probability=True)
svm.fit(X_train_s, y_train)

# Evaluate with probabilities
probs = svm.predict_proba(X_test_s)
for i, prob in enumerate(probs):
    top_idx = np.argmax(prob)
    top_celeb = list(class_dict.keys())[list(class_dict.values()).index(top_idx)]
    print(f"Sample {i}: Predicted '{top_celeb}' with {prob[top_idx]*100:.2f}% confidence")

# Evaluate
y_pred = svm.predict(X_test_s)
print("Test accuracy:", svm.score(X_test_s, y_test))
print(classification_report(y_test, y_pred, target_names=sorted(class_dict.keys())))

# Save model, scaler, and class dict
joblib.dump({'svm': svm, 'scaler': scaler, 'class_dict': class_dict}, model_out)
print(f"Saved model to {model_out}")
