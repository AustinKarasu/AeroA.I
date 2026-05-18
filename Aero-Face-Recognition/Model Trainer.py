import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from face_recognition_tools import train_model


print('Training faces. It will take a few seconds. Wait ...')
sample_count, user_ids = train_model()
print(f'Model trained with {sample_count} samples for user IDs: {user_ids}.')
