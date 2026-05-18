# Aero Face Recognition

This module captures face samples, trains an LBPH model, and recognizes the trained user from the webcam.

## Requirements

Install the main project requirements first:

```powershell
pip install -r ..\requirements.txt
```

The important package is `opencv-contrib-python`, because the normal OpenCV package does not include `cv2.face`.

## How to Train

Run these commands from the project root:

```powershell
.\.venv\Scripts\python.exe "Aero-Face-Recognition\Sample generator.py"
.\.venv\Scripts\python.exe "Aero-Face-Recognition\Model Trainer.py"
.\.venv\Scripts\python.exe "Aero-Face-Recognition\Face recognition.py"
```

Use a numeric ID such as `1` and a readable name such as `Aayan`. The camera window opens while samples are captured. Press `ESC` to stop early.

## Notes

Face samples are private biometric data. Keep them local and do not upload personal training samples to public repositories.
