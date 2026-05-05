"""Reglas biomecánicas para los 3 puntos de contacto: sillín, manos, pies."""

from app.models import ContactPoints, Discipline, Recommendation, Severity

# Rangos ideales por disciplina: (min, max) grados
RULES: dict[Discipline, dict] = {
    Discipline.ROAD: {
        "saddle_knee_angle": {"range": (140.0, 150.0), "point": "saddle", "adj_low": "Subir sillín 5-10mm", "adj_high": "Bajar sillín 5-10mm"},
        "saddle_hip_angle": {"range": (70.0, 80.0), "point": "saddle", "adj_low": "Adelantar sillín", "adj_high": "Retrasar sillín"},
        "hands_back_angle": {"range": (35.0, 45.0), "point": "hands", "adj_low": "Subir manillar o acortar potencia", "adj_high": "Bajar manillar o alargar potencia"},
        "hands_elbow_angle": {"range": (150.0, 170.0), "point": "hands", "adj_low": "Acortar potencia (reach excesivo)", "adj_high": "Alargar potencia (muy cerca del manillar)"},
        "feet_ankle_angle": {"range": (95.0, 115.0), "point": "feet", "adj_low": "Revisar posición de cala (muy adelantada)", "adj_high": "Revisar posición de cala (muy retrasada)"},
    },
    Discipline.MTB: {
        "saddle_knee_angle": {"range": (135.0, 150.0), "point": "saddle", "adj_low": "Subir sillín 5-10mm", "adj_high": "Bajar sillín 5-10mm"},
        "saddle_hip_angle": {"range": (65.0, 80.0), "point": "saddle", "adj_low": "Adelantar sillín", "adj_high": "Retrasar sillín"},
        "hands_back_angle": {"range": (40.0, 55.0), "point": "hands", "adj_low": "Subir manillar", "adj_high": "Bajar manillar"},
        "hands_elbow_angle": {"range": (140.0, 165.0), "point": "hands", "adj_low": "Acortar potencia", "adj_high": "Alargar potencia"},
        "feet_ankle_angle": {"range": (90.0, 115.0), "point": "feet", "adj_low": "Revisar posición de cala", "adj_high": "Revisar posición de cala"},
    },
    Discipline.TT: {
        "saddle_knee_angle": {"range": (140.0, 150.0), "point": "saddle", "adj_low": "Subir sillín 5-10mm", "adj_high": "Bajar sillín 5-10mm"},
        "saddle_hip_angle": {"range": (65.0, 75.0), "point": "saddle", "adj_low": "Adelantar sillín", "adj_high": "Retrasar sillín"},
        "hands_back_angle": {"range": (20.0, 35.0), "point": "hands", "adj_low": "Subir acoples", "adj_high": "Bajar acoples"},
        "hands_elbow_angle": {"range": (90.0, 110.0), "point": "hands", "adj_low": "Acercar acoples", "adj_high": "Alejar acoples"},
        "feet_ankle_angle": {"range": (95.0, 115.0), "point": "feet", "adj_low": "Revisar posición de cala", "adj_high": "Revisar posición de cala"},
    },
}


def evaluate(points: ContactPoints, discipline: Discipline) -> list[Recommendation]:
    """Evalúa los 3 puntos de contacto y genera recomendaciones de ajuste."""
    rules = RULES[discipline]
    recs = []
    for metric, rule in rules.items():
        value = getattr(points, metric)
        lo, hi = rule["range"]
        if value < lo:
            severity = Severity.CRITICAL if value < lo - 10 else Severity.WARNING
            msg = rule["adj_low"]
        elif value > hi:
            severity = Severity.CRITICAL if value > hi + 10 else Severity.WARNING
            msg = rule["adj_high"]
        else:
            severity = Severity.OK
            msg = "Correcto"
        recs.append(Recommendation(
            contact_point=rule["point"],
            metric=metric, value=round(value, 1),
            ideal_range=(lo, hi), severity=severity,
            adjustment=rule["point"], message=msg,
        ))
    return recs
