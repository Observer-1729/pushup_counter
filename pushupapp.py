import cv2
import mediapipe as mp
import numpy as np

import tkinter as tk
from tkinter import filedialog,messagebox



from mediapipe.tasks.python import vision
from mediapipe.tasks.python.core.base_options import BaseOptions

# =========================
# ANGLE FUNCTION
# =========================
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
              np.arctan2(a[1]-b[1], a[0]-b[0])

    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle

class PushupDetector:

    def __init__(self, model_path="pose_landmarker_lite.task"):
        from mediapipe.tasks.python import vision
        from mediapipe.tasks.python.core.base_options import BaseOptions


        base_options = BaseOptions(model_asset_path=model_path)

        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO
        )

        self.landmarker = vision.PoseLandmarker.create_from_options(options)

    def videocapture(self , source=0):

        cap = cv2.VideoCapture(source)

        if not cap.isOpened():
            print("Error: Cannot open video source")
            return 0

        frame_width = 640
        frame_height = 480

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0:
            fps = 30  # fallback for webcam

        # =========================
        # VARIABLES
        # =========================
        counter = 0
        prev_y = None

        angle_history = []
        y_history = []

        rep_stage = "idle"
        rep_valid = True
        rep_min_angle = 180
        rep_max_angle = 0

        frame_timestamp = 0

        connections = [
            (0, 11), (0, 12),
            (11, 13), (13, 15),
            (12, 14), (14, 16),
            (11, 12),
            (11, 23), (12, 24),
            (23, 24),
            (23, 25), (25, 27),
            (24, 26), (26, 28),
        ]

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_timestamp = 0

        # =========================
        # LOOP
        # =========================
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (frame_width, frame_height))

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

            timestamp = int((frame_timestamp / fps) * 1000)
            result = self.landmarker.detect_for_video(mp_image, timestamp)
            frame_timestamp += 1

            if result.pose_landmarks:
                for pose in result.pose_landmarks:
                    h, w, _ = frame.shape

                    # SIDE SELECTION
                    r_shoulder, r_elbow, r_wrist = pose[12], pose[14], pose[16]
                    l_shoulder, l_elbow, l_wrist = pose[11], pose[13], pose[15]

                    right_vis = (r_shoulder.visibility + r_elbow.visibility + r_wrist.visibility) / 3
                    left_vis  = (l_shoulder.visibility + l_elbow.visibility + l_wrist.visibility) / 3

                    if right_vis > left_vis:
                        shoulder, elbow, wrist = r_shoulder, r_elbow, r_wrist
                        hip, ankle = pose[24], pose[28]
                    else:
                        shoulder, elbow, wrist = l_shoulder, l_elbow, l_wrist
                        hip, ankle = pose[23], pose[27]

                    # ANGLES
                    a = [shoulder.x*w, shoulder.y*h]
                    b = [elbow.x*w, elbow.y*h]
                    c = [wrist.x*w, wrist.y*h]

                    angle = calculate_angle(a, b, c)

                    a_body = [shoulder.x*w, shoulder.y*h]
                    b_body = [hip.x*w, hip.y*h]
                    c_body = [ankle.x*w, ankle.y*h]

                    body_angle = calculate_angle(a_body, b_body, c_body)

                    is_straight = 165 < body_angle < 180

                    # SMOOTHING
                    angle_history.append(angle)
                    if len(angle_history) > 5:
                        angle_history.pop(0)
                    smooth_angle = np.mean(angle_history)

                    shoulder_y = shoulder.y * h
                    y_history.append(shoulder_y)
                    if len(y_history) > 5:
                        y_history.pop(0)
                    smooth_y = np.mean(y_history)

                    # MOVEMENT
                    if prev_y is not None:
                        if smooth_y > prev_y:
                            direction = "down"
                        else:
                            direction = "up"
                    prev_y = smooth_y

                    # =========================
                    # REP LOGIC (FINAL)
                    # =========================
                    rep_min_angle = min(rep_min_angle, smooth_angle)
                    rep_max_angle = max(rep_max_angle, smooth_angle)

                    if not is_straight:
                        rep_valid = False

                    if smooth_angle < 90 and rep_stage == "idle":
                        rep_stage = "down"

                    if smooth_angle > 110 and rep_stage == "down":
                        rep_stage = "up"

                        if rep_valid and rep_min_angle < 85 and rep_max_angle > 110:
                            counter += 1

                        # reset
                        rep_stage = "idle"
                        rep_valid = True
                        rep_min_angle = 180
                        rep_max_angle = 0

                    # DRAW
                    for lm in pose:
                        x, y = int(lm.x*w), int(lm.y*h)
                        cv2.circle(frame, (x,y), 4, (0,255,0), -1)

                    for c in connections:
                        x1,y1 = int(pose[c[0]].x*w), int(pose[c[0]].y*h)
                        x2,y2 = int(pose[c[1]].x*w), int(pose[c[1]].y*h)
                        cv2.line(frame, (x1,y1), (x2,y2), (255,0,0), 2)


            # cv2.imshow("Push-up Detection", frame)

            # if cv2.waitKey(1) & 0xFF == 27:
            #     break

        cap.release()
        cv2.destroyAllWindows()

        return counter
    

# import tkinter as tk
# from tkinter import messagebox, filedialog

def final_fun():
    root = tk.Tk()
    root.withdraw()

    messagebox.showinfo(
        "Upload Guidelines",
        "• Keep camera at SIDE VIEW (90°)\n"
        "• Full body should be visible\n"
        "• Avoid front/top angles\n"
        "• Ensure good lighting\n"
        "• Keep camera stable"
    )

    file_path = filedialog.askopenfilename(
        title="Select a video file",
        filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv")]
    )

    if not file_path:
        print("No file selected")
        return

    detector = PushupDetector()
    count = detector.videocapture(file_path)

    print("Push-ups counted:", count)

final_fun()
