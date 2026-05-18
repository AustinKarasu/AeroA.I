import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from face_recognition_tools import capture_samples


face_id = input('Enter a numeric user ID: ').strip()
face_name = input('Enter user name: ').strip()

print('Taking samples. Look at the camera and press ESC to stop early.')
count = capture_samples(face_id, face_name, sample_count=50)
print(f'Captured {count} samples. Now run Model Trainer.py.')
