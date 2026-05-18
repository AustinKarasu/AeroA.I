from pathlib import Path
import json
import os
import time

import cv2
import numpy as np
from PIL import Image


BASE_DIR = Path(__file__).resolve().parent
FACE_DIR = BASE_DIR / 'Aero-Face-Recognition'
SAMPLES_DIR = FACE_DIR / 'samples'
TRAINER_DIR = FACE_DIR / 'trainer'
TRAINER_PATH = TRAINER_DIR / 'trainer.yml'
LABELS_PATH = TRAINER_DIR / 'labels.json'
CASCADE_PATH = FACE_DIR / 'haarcascade_frontalface_default.xml'


class FaceRecognitionError(RuntimeError):
    pass


def ensure_face_module():
    if not hasattr(cv2, 'face'):
        raise FaceRecognitionError(
            'OpenCV face recognition is unavailable. Install opencv-contrib-python from requirements.txt.'
        )


def load_detector():
    if not CASCADE_PATH.exists():
        raise FaceRecognitionError('Face cascade file is missing: ' + str(CASCADE_PATH))
    detector = cv2.CascadeClassifier(str(CASCADE_PATH))
    if detector.empty():
        raise FaceRecognitionError('Face cascade could not be loaded.')
    return detector


def open_camera(camera_index=0):
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, 0] if os.name == 'nt' else [0]
    for backend in backends:
        cam = cv2.VideoCapture(camera_index, backend) if backend else cv2.VideoCapture(camera_index)
        if cam.isOpened():
            cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            return cam
        cam.release()
    raise FaceRecognitionError('Camera is not available.')


def load_labels():
    if LABELS_PATH.exists():
        try:
            with LABELS_PATH.open(encoding='utf-8') as labels_file:
                data = json.load(labels_file)
            return {int(key): value for key, value in data.items()}
        except Exception:
            return {}
    return {}


def save_labels(labels):
    TRAINER_DIR.mkdir(exist_ok=True)
    with LABELS_PATH.open('w', encoding='utf-8') as labels_file:
        json.dump({str(key): value for key, value in labels.items()}, labels_file, indent=2)


def capture_samples(user_id, user_name, sample_count=50, camera_index=0):
    if not str(user_id).isdigit():
        raise FaceRecognitionError('User ID must be numeric.')

    detector = load_detector()
    SAMPLES_DIR.mkdir(exist_ok=True)
    user_id = int(user_id)
    labels = load_labels()
    labels[user_id] = user_name.strip() or ('User ' + str(user_id))
    save_labels(labels)

    cam = open_camera(camera_index)
    count = 0
    try:
        while count < sample_count:
            ok, frame = cam.read()
            if not ok or frame is None:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
            for (x, y, w, h) in faces:
                count += 1
                cv2.imwrite(str(SAMPLES_DIR / f'face.{user_id}.{count}.jpg'), gray[y:y+h, x:x+w])
                cv2.rectangle(frame, (x, y), (x+w, y+h), (34, 199, 231), 2)
                cv2.putText(
                    frame,
                    f'Sample {count}/{sample_count}',
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (34, 199, 231),
                    2,
                )
            cv2.imshow('Aero face sample capture', frame)
            key = cv2.waitKey(80) & 0xFF
            if key == 27:
                break
    finally:
        cam.release()
        cv2.destroyAllWindows()

    if count == 0:
        raise FaceRecognitionError('No face samples were captured.')
    return count


def train_model():
    ensure_face_module()
    detector = load_detector()
    if not SAMPLES_DIR.exists():
        raise FaceRecognitionError('No samples folder found. Run sample capture first.')

    face_samples = []
    ids = []
    for image_path in sorted(SAMPLES_DIR.glob('face.*.*.jpg')):
        parts = image_path.stem.split('.')
        if len(parts) < 3 or not parts[1].isdigit():
            continue
        user_id = int(parts[1])
        gray_img = Image.open(image_path).convert('L')
        img_arr = np.array(gray_img, 'uint8')
        faces = detector.detectMultiScale(img_arr)
        if len(faces) == 0:
            face_samples.append(img_arr)
            ids.append(user_id)
            continue
        for (x, y, w, h) in faces:
            face_samples.append(img_arr[y:y+h, x:x+w])
            ids.append(user_id)

    if not face_samples:
        raise FaceRecognitionError('No usable face samples found.')

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(face_samples, np.array(ids))
    TRAINER_DIR.mkdir(exist_ok=True)
    recognizer.write(str(TRAINER_PATH))
    return len(face_samples), sorted(set(ids))


def load_recognizer():
    ensure_face_module()
    if not TRAINER_PATH.exists():
        raise FaceRecognitionError('Trainer file is missing. Capture samples and train the model first.')
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(str(TRAINER_PATH))
    return recognizer


def recognize_once(timeout_seconds=15, confidence_threshold=65, camera_index=0, show_window=False):
    recognizer = load_recognizer()
    detector = load_detector()
    labels = load_labels()
    cam = open_camera(camera_index)
    deadline = time.time() + timeout_seconds
    best = None

    try:
        while time.time() < deadline:
            ok, frame = cam.read()
            if not ok or frame is None:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            min_w = max(30, int(0.1 * cam.get(cv2.CAP_PROP_FRAME_WIDTH)))
            min_h = max(30, int(0.1 * cam.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            faces = detector.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(min_w, min_h))
            for (x, y, w, h) in faces:
                user_id, distance = recognizer.predict(gray[y:y+h, x:x+w])
                confidence = max(0, min(100, round(100 - distance)))
                name = labels.get(user_id, 'User ' + str(user_id))
                best = {
                    'recognized': distance <= confidence_threshold,
                    'user_id': user_id,
                    'name': name,
                    'confidence': confidence,
                }
                if show_window:
                    color = (34, 199, 231) if best['recognized'] else (80, 80, 255)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                    cv2.putText(
                        frame,
                        name if best['recognized'] else 'Unknown',
                        (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        color,
                        2,
                    )
                    cv2.imshow('Aero face recognition', frame)
                    cv2.waitKey(1)
                if best['recognized']:
                    return best
            if show_window:
                cv2.imshow('Aero face recognition', frame)
                if cv2.waitKey(10) & 0xFF == 27:
                    break
    finally:
        cam.release()
        cv2.destroyAllWindows()

    return best or {'recognized': False, 'user_id': None, 'name': None, 'confidence': 0}
