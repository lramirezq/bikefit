"""Procesador de video: extrae los 3 puntos de contacto con MediaPipe y genera frame anotado."""

import base64

import cv2
import mediapipe as mp
import numpy as np

from app.engine.angles import angle_between, back_angle
from app.models import ContactPoints, Discipline, FitResult
from app.engine.rules import evaluate

mp_pose = mp.solutions.pose
LM = mp_pose.PoseLandmark


def _lm(landmark) -> np.ndarray:
    return np.array([landmark.x, landmark.y])


def _draw_annotated_frame(frame, landmarks, angles: ContactPoints):
    """Dibuja esqueleto y ángulos sobre un frame."""
    h, w = frame.shape[:2]
    lm = landmarks.landmark

    def px(landmark):
        return int(lm[landmark].x * w), int(lm[landmark].y * h)

    # Puntos clave
    pts = {
        'hip': px(LM.RIGHT_HIP), 'knee': px(LM.RIGHT_KNEE),
        'ankle': px(LM.RIGHT_ANKLE), 'shoulder': px(LM.RIGHT_SHOULDER),
        'elbow': px(LM.RIGHT_ELBOW), 'wrist': px(LM.RIGHT_WRIST),
        'foot': px(LM.RIGHT_FOOT_INDEX),
    }

    # Dibujar huesos
    bones = [('shoulder', 'hip'), ('hip', 'knee'), ('knee', 'ankle'),
             ('ankle', 'foot'), ('shoulder', 'elbow'), ('elbow', 'wrist')]
    for a, b in bones:
        cv2.line(frame, pts[a], pts[b], (0, 255, 200), 3)

    # Dibujar articulaciones
    for pt in pts.values():
        cv2.circle(frame, pt, 6, (0, 200, 255), -1)

    # Dibujar ángulos con texto
    labels = [
        (pts['knee'], f"{angles.saddle_knee_angle:.0f}°", "Rodilla"),
        (pts['hip'], f"{angles.saddle_hip_angle:.0f}°", "Cadera"),
        (pts['elbow'], f"{angles.hands_elbow_angle:.0f}°", "Codo"),
        (pts['ankle'], f"{angles.feet_ankle_angle:.0f}°", "Tobillo"),
    ]
    for pt, angle_text, name in labels:
        # Arco indicador
        cv2.putText(frame, f"{name}: {angle_text}", (pt[0] + 10, pt[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Ángulo espalda (texto en el torso)
    mid_back = ((pts['shoulder'][0] + pts['hip'][0]) // 2, (pts['shoulder'][1] + pts['hip'][1]) // 2)
    cv2.putText(frame, f"Espalda: {angles.hands_back_angle:.0f}°", (mid_back[0] + 10, mid_back[1]),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    return frame


def process_video(video_path: str, discipline: Discipline = Discipline.ROAD) -> FitResult:
    """Procesa video, mide los 3 puntos de contacto y genera frame anotado."""
    cap = cv2.VideoCapture(video_path)
    all_points: list[ContactPoints] = []
    mid_frame = None
    mid_landmarks = None
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    mid_target = total_frames // 2

    frame_idx = 0
    with mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if not results.pose_landmarks:
                frame_idx += 1
                continue

            lm = results.pose_landmarks.landmark
            hip = _lm(lm[LM.RIGHT_HIP])
            knee = _lm(lm[LM.RIGHT_KNEE])
            ankle = _lm(lm[LM.RIGHT_ANKLE])
            shoulder = _lm(lm[LM.RIGHT_SHOULDER])
            elbow = _lm(lm[LM.RIGHT_ELBOW])
            wrist = _lm(lm[LM.RIGHT_WRIST])
            foot = _lm(lm[LM.RIGHT_FOOT_INDEX])

            points = ContactPoints(
                saddle_knee_angle=angle_between(hip, knee, ankle),
                saddle_hip_angle=angle_between(shoulder, hip, knee),
                hands_elbow_angle=angle_between(shoulder, elbow, wrist),
                hands_back_angle=back_angle(shoulder, hip),
                feet_ankle_angle=angle_between(knee, ankle, foot),
            )
            all_points.append(points)

            # Guardar frame del medio para anotar
            if frame_idx >= mid_target and mid_frame is None:
                mid_frame = frame.copy()
                mid_landmarks = results.pose_landmarks

            frame_idx += 1

    cap.release()

    if not all_points:
        raise ValueError("No se detectó pose en ningún frame del video.")

    avg = ContactPoints(
        saddle_knee_angle=float(np.mean([p.saddle_knee_angle for p in all_points])),
        saddle_hip_angle=float(np.mean([p.saddle_hip_angle for p in all_points])),
        hands_elbow_angle=float(np.mean([p.hands_elbow_angle for p in all_points])),
        hands_back_angle=float(np.mean([p.hands_back_angle for p in all_points])),
        feet_ankle_angle=float(np.mean([p.feet_ankle_angle for p in all_points])),
    )

    # Generar imagen anotada
    annotated_b64 = None
    if mid_frame is not None and mid_landmarks is not None:
        annotated = _draw_annotated_frame(mid_frame, mid_landmarks, avg)
        _, buf = cv2.imencode('.jpg', annotated, [cv2.IMWRITE_JPEG_QUALITY, 80])
        annotated_b64 = base64.b64encode(buf).decode('utf-8')

    return FitResult(
        contact_points=avg,
        recommendations=evaluate(avg, discipline),
        frames_analyzed=len(all_points),
        annotated_frame=annotated_b64,
    )
