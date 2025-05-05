# Celebrity Face Recognition AI

This project is a web application that allows users to upload images and predict the celebrity they resemble. It uses FaceNet for facial recognition and SVM (Support Vector Machine) for celebrity identification. Users can log in or use the system as a guest. Predicted results are displayed after image upload.

## Features
- **User Authentication**: Users can register, log in, and log out.
- **Guest Mode**: Users can upload images as guests without registering or logging in.
- **Image Upload and Prediction**: After uploading an image, the system predicts the celebrity's name based on facial recognition.
- **Image Storage**: Uploads and their predicted results are stored in the database.
- **Profile Management**: Logged-in users have personalized image uploads linked to their profiles.

## Requirements

- Python 3.8 or above
- Django 5.2
- PostgreSQL (or SQLite for local development)
- `facenet_pytorch` library for facial recognition

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/celebrity-face-recognition.git
   cd celebrity-face-recognition
