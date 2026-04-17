import cv2
import numpy as np
import mediapipe as mp

mp_pose = mp.solutions.pose


def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180 else angle


def analyze_video(video_path, camera="Side View"):

    pose = mp_pose.Pose()
    cap = cv2.VideoCapture(video_path)

    frame_id = 0

    # store frame-level data (IMPORTANT FIX)
    frame_data = []
    wrist_positions = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(rgb)

        if result.pose_landmarks:

            lm = result.pose_landmarks.landmark

            # visibility check
            if min(
                lm[12].visibility,
                lm[14].visibility,
                lm[16].visibility,
                lm[24].visibility,
                lm[26].visibility,
                lm[28].visibility
            ) < 0.6:
                frame_id += 1
                continue

            shoulder = lm[12]
            elbow = lm[14]
            wrist = lm[16]

            hip = lm[24]
            knee = lm[26]
            ankle = lm[28]

            wrist_pt = np.array([wrist.x, wrist.y])
            wrist_positions.append((frame_id, wrist_pt))

            arm_angle = calculate_angle(
                [shoulder.x, shoulder.y],
                [elbow.x, elbow.y],
                [wrist.x, wrist.y]
            )

            knee_angle = calculate_angle(
                [hip.x, hip.y],
                [knee.x, knee.y],
                [ankle.x, ankle.y]
            )

            # range filter
            if not (110 < arm_angle < 240 and 100 < knee_angle < 200):
                frame_id += 1
                continue

            # store frame-level aligned data
            frame_data.append({
                "frame": frame_id,
                "arm": arm_angle,
                "knee": knee_angle
            })

        frame_id += 1

    cap.release()

    # -------- VALIDATION --------
    if len(frame_data) < 10:
        return {"error": "Low visibility or incomplete body"}

    if len(wrist_positions) < 5:
        return {"error": "Insufficient motion detected"}

    # -------- RELEASE DETECTION --------
    speeds = []

    for i in range(1, len(wrist_positions)):
        prev_frame, prev_pt = wrist_positions[i-1]
        curr_frame, curr_pt = wrist_positions[i]

        speed = np.linalg.norm(curr_pt - prev_pt)
        speeds.append((curr_frame, speed))

    if not speeds:
        return {"error": "Motion detection failed"}

    # find max speed frame
    release_frame = max(speeds, key=lambda x: x[1])[0]

    # -------- SELECT WINDOW --------
    window_frames = range(release_frame - 5, release_frame + 6)

    arm_window = []
    knee_window = []

    for data in frame_data:
        if data["frame"] in window_frames:
            arm_window.append(data["arm"])
            knee_window.append(data["knee"])

    if len(arm_window) < 3 or len(knee_window) < 3:
        return {"error": "Release phase not captured clearly"}

    # -------- OUTLIER REMOVAL --------
    def remove_outliers(data):
        if len(data) < 5:
            return data
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        return [x for x in data if (q1 - 1.5*iqr) <= x <= (q3 + 1.5*iqr)]

    arm_window = remove_outliers(arm_window)
    knee_window = remove_outliers(knee_window)

    # -------- FINAL VALUES --------
    avg_arm = float(np.median(arm_window))
    avg_knee = float(np.median(knee_window))

    # -------- CLASSIFICATION --------
    if avg_arm < 170:
        arm_type = "Low Arm Action"
        arm_feedback = "Arm too low → reduces bounce and effectiveness"
    elif avg_arm < 190:
        arm_type = "Side Arm Action"
        arm_feedback = "Moderate arm → can improve height"
    else:
        arm_type = "High Arm Action"
        arm_feedback = "Strong arm → good bounce and control"

    if avg_knee < 145:
        knee_feedback = "Front knee collapsing → reduces power and increases injury risk"
        knee_quality = "Weak"
    elif avg_knee < 165:
        knee_feedback = "Moderate stability → improve bracing"
        knee_quality = "Moderate"
    else:
        knee_feedback = "Strong front leg → good energy transfer"
        knee_quality = "Strong"

    knee_risk = avg_knee < 145
    shoulder_risk = avg_arm > 200

    arm_variation = np.std(arm_window)

    if arm_variation < 5:
        consistency = "Highly consistent"
    elif arm_variation < 10:
        consistency = "Moderate consistency"
    else:
        consistency = "Inconsistent action"

    return {
        "arm_angle": round(avg_arm, 2),
        "knee_angle": round(avg_knee, 2),
        "arm_type": arm_type,
        "knee_quality": knee_quality,
        "knee_risk": bool(knee_risk),
        "shoulder_risk": bool(shoulder_risk),
        "consistency": consistency,
        "arm_feedback": arm_feedback,
        "knee_feedback": knee_feedback,
        "release_frame": int(release_frame)
    }