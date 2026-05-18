import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from face_recognition_tools import recognize_once


print('Starting Aero face recognition. Press ESC in the camera window to stop.')
result = recognize_once(timeout_seconds=60, confidence_threshold=65, show_window=True)
if result['recognized']:
    print(f"Recognized {result['name']} with {result['confidence']}% confidence.")
else:
    print('Face detected but not recognized, or no face was found.')
