"""Motor de cálculo de ángulos en los 3 puntos de contacto."""

import numpy as np


def angle_between(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """Ángulo en el punto b formado por vectores ba y bc (grados)."""
    ba = a - b
    bc = c - b
    cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8)
    return float(np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0))))


def back_angle(shoulder: np.ndarray, hip: np.ndarray) -> float:
    """Ángulo del torso respecto a la horizontal."""
    diff = shoulder - hip
    return float(np.degrees(np.arctan2(abs(diff[1]), abs(diff[0]))))
