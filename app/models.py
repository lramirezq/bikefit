from enum import Enum
from pydantic import BaseModel


class Discipline(str, Enum):
    ROAD = "road"
    MTB = "mtb"
    TT = "tt"


class Severity(str, Enum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"


class ContactPoints(BaseModel):
    """Ángulos medidos en los 3 puntos de contacto."""
    saddle_knee_angle: float  # extensión rodilla → indica altura sillín
    saddle_hip_angle: float  # ángulo cadera → indica retroceso sillín
    hands_elbow_angle: float  # ángulo codo → indica reach/drop manillar
    hands_back_angle: float  # ángulo espalda → indica relación sillín-manillar
    feet_ankle_angle: float  # ángulo tobillo → indica posición pie en pedal


class Recommendation(BaseModel):
    contact_point: str  # "saddle", "hands", "feet"
    metric: str
    value: float
    ideal_range: tuple[float, float]
    severity: Severity
    adjustment: str  # qué ajustar
    message: str


class FitResult(BaseModel):
    contact_points: ContactPoints
    recommendations: list[Recommendation]
    frames_analyzed: int
    annotated_frame: str | None = None  # imagen JPG en base64
