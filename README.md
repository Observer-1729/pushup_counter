# Push-up Counter 💪

A computer vision project that counts push-ups in video footage using **Python, OpenCV, MediaPipe, and NumPy**.

## Features

- Detects body landmarks with MediaPipe Pose Landmarker.
- Calculates elbow and body angles to track push-up movement.
- Smooths landmark measurements to reduce frame-to-frame fluctuations.
- Counts repetitions that meet the configured movement and body-alignment thresholds.
- Accepts uploaded video files for analysis.

## Tech Stack

- Python
- OpenCV
- MediaPipe Pose Landmarker
- NumPy
- Tkinter

## How It Works

The application processes a selected video frame by frame, detects pose landmarks, and calculates elbow and body angles. It uses these measurements to identify the down-and-up phases of a push-up and counts repetitions that meet the configured conditions.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Observer-1729/pushup_counter.git
cd pushup_counter
```

### 2. Install dependencies

```bash
pip install opencv-python mediapipe numpy
```

Tkinter is included with many Python installations. On some Linux distributions, it must be installed separately.

### 3. Download the pose model

Download the **MediaPipe Pose Landmarker Lite** task model and save it in the project directory as:

```text
pose_landmarker_lite.task
```

The script expects this file by default.

### 4. Run the application

```bash
python pushupapp.py
```

Select a supported video file when prompted. After processing, the push-up count is printed in the terminal.

## Repository Contents

- `pushupapp.py` — Python implementation of the push-up counter.
- `pushupapp.ipynb` — Jupyter Notebook version.
- Sample videos — video files for testing and experimentation.

## Limitations

- Counting accuracy depends on camera angle, lighting, video quality, and visible body landmarks.
- The current workflow processes video files; live webcam counting is not enabled in the provided implementation.
- The video preview and on-screen landmark display are currently disabled in the script.
- Angle thresholds may need adjustment for different users or push-up variations.

## Future Improvements

- Display annotated video and the live repetition count.
- Add a graphical results screen.
- Support real-time webcam counting.
- Provide more detailed form feedback.

---

Built with Python and computer vision to explore pose estimation and movement analysis.
