import cv2
import dlib
import numpy as np
import os
from django.http import HttpResponse

from django.http import JsonResponse
from rest_framework.decorators import api_view

# Define paths to your dlib data files
PREDICTOR_PATH = r"shape_predictor_68_face_landmarks.dat"
FACE_RECOGNITION_MODEL_PATH = (
    r"dlib_face_recognition_resnet_model_v1.dat"
)

# Load the models


# Initialize dlib's face detector and predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(PREDICTOR_PATH)
face_recognition_model = dlib.face_recognition_model_v1(FACE_RECOGNITION_MODEL_PATH)


def save_uploaded_file(uploaded_file, filename):
    """Save the uploaded file to a specified path."""
    with open(filename, "wb+") as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    return filename


def extract_face_from_frame(frame):
    """Extract a face from a video frame."""
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray_frame)

    if len(faces) == 0:
        return None, None  # Return None if no faces are found

    face = faces[0]  # Take the first detected face
    landmarks = predictor(gray_frame, face)

    # Extract face chip to ensure proper alignment and size
    face_chip = dlib.get_face_chip(frame, landmarks, size=150)

    return face_chip


def extract_face_from_video(file_path):
    """Extract the first frame's face from a video."""
    video_capture = cv2.VideoCapture(file_path)
    success, frame = video_capture.read()

    if not success:
        raise ValueError("Failed to read the video frame.")

    face_image = extract_face_from_frame(frame)
    video_capture.release()

    return face_image


def extract_face_descriptor(face_image):
    """Extract face descriptor from a face image."""
    if face_image is None:
        return None

    # Convert face image to RGB (dlib uses RGB)
    face_image_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
    return face_recognition_model.compute_face_descriptor(face_image_rgb)


def compare_faces(face1, face2):
    """Compare two faces and return whether they match."""
    face1_descriptor = extract_face_descriptor(face1)
    face2_descriptor = extract_face_descriptor(face2)

    if face1_descriptor is None or face2_descriptor is None:
        return False

    # Convert to numpy arrays for distance calculation
    face1_descriptor = np.array(face1_descriptor)
    face2_descriptor = np.array(face2_descriptor)

    distance = np.linalg.norm(face1_descriptor - face2_descriptor)
    return distance < 0.6  # Adjust this threshold as needed


@api_view(["POST"])
def compare_videos(request):
    """Handle POST request to compare faces in two video files."""
    if "video1" not in request.FILES or "video2" not in request.FILES:
        return JsonResponse(
            {"error": "Both video1 and video2 files must be provided."}, status=400
        )

    video1 = request.FILES["video1"]
    video2 = request.FILES["video2"]

    video1_path = "temp_video1.mp4"
    video2_path = "temp_video2.mp4"

    try:
        save_uploaded_file(video1, video1_path)
        save_uploaded_file(video2, video2_path)

        face1 = extract_face_from_video(video1_path)
        face2 = extract_face_from_video(video2_path)

        if face1 is None or face2 is None:
            return JsonResponse(
                {"error": "No face found in one or both videos."}, status=400
            )

        match = compare_faces(face1, face2)

        if match:
            return JsonResponse({"message": "Faces match successfully."})
        else:
            return JsonResponse({"message": "Faces do not match."})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    finally:
        if os.path.exists(video1_path):
            os.remove(video1_path)
        if os.path.exists(video2_path):
            os.remove(video2_path)
@api_view(["GET"])
def filter_pdf():
    # Assuming you want to process the PDF or perform some logic here
    # For now, just return a static JSON response
    return JsonResponse({"message": "Faces do not match."})

def home(request):
    return HttpResponse("Welcome to the home page!")

# login
# email


# public function register(Request $request)
#     {
#         $request->validate([
#             'name' => 'required|string|max:255',
#             'email' => 'required|string|email|max:255|unique:users',
#             'password' => 'required|string|confirmed|min:8',
#             'face_video' => 'required|file|mimes:mp4,avi|max:20000' // Validate video file
#         ]);

#         $path = $request->file('face_video')->store('face_videos');

#         $user = User::create([
#             'name' => $request->name,
#             'email' => $request->email,
#             'password' => Hash::make($request->password),
#             'face_video_path' => $path
#         ]);
#         return response()->json(['message' => 'User registered successfully']);
#     }


# public function login(Request $request)
#     {
#         $request->validate([
#             'email' => 'required|string|email',
#             'password' => 'required|string',
#             'login_video' => 'required|file|mimes:mp4,avi|max:20000' // Validate video file
#         ]);

#         $credentials = $request->only('email', 'password');

#         if (Auth::attempt($credentials)) {
#             $user = Auth::user();
#             $loginVideoPath = $request->file('login_video')->store('login_videos');

#             // Compare videos using API
#             $response = Http::post('localhost:8000/api/compare-videos/', [
#                 'video1' => Storage::path($user->face_video_path),
#                 'video2' => Storage::path($loginVideoPath)
#             ]);

#             if ($response->json('match')) {
#                 return response()->json(['message' => 'Login successful']);
#             } else {
#                 return response()->json(['message' => 'Face mismatch'], 401);
#             }
#         }

#         return response()->json(['message' => 'Invalid credentials'], 401);
#     }
