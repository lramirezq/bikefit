# 🚴 BikeFit

Análisis biomecánico de posición en bicicleta usando visión por computador. Graba un video lateral del ciclista en el rodillo y obtén recomendaciones de ajuste para los 3 puntos de contacto: sillín, manos y pies.

## Qué hace

- **Detecta pose** del ciclista usando MediaPipe Pose (33 landmarks)
- **Calcula ángulos** en los puntos clave: rodilla, cadera, codo, espalda y tobillo
- **Evalúa** los ángulos contra rangos biomecánicos ideales según disciplina (ruta, MTB, contrarreloj)
- **Genera recomendaciones** accionables: subir/bajar sillín, ajustar potencia, revisar calas
- **Muestra frame anotado** con el esqueleto y los ángulos dibujados sobre la imagen real

## Puntos de contacto analizados

| Punto | Métricas | Ajustes sugeridos |
|-------|----------|-------------------|
| 🪑 Sillín | Extensión rodilla, ángulo cadera | Altura y retroceso del sillín |
| 🤲 Manos | Ángulo espalda, ángulo codo | Altura/longitud de potencia y manillar |
| 🦶 Pies | Ángulo tobillo | Posición de calas en el pedal |

## Requisitos

- Python 3.11 (MediaPipe no soporta 3.13 aún)
- Cámara (móvil o webcam)

## Instalación

```bash
git clone git@github.com:lramirezq/bikefit.git
cd bikefit
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Uso

```bash
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Abrir en el navegador: http://localhost:8001

### Desde el móvil

Para acceder desde el móvil (necesario para grabar con la cámara trasera):

```bash
# Opción 1: misma red WiFi
# Abrir http://<IP-DE-TU-MAC>:8001

# Opción 2: ngrok (recomendado, da HTTPS para acceso a cámara en iOS)
ngrok http 8001
# Abrir la URL https://xxx.ngrok-free.dev en el móvil
```

## Cómo grabar

1. Coloca el móvil **horizontal** a la **altura del eje del pedalier**, a **2-3 metros** de distancia
2. Graba el **lado derecho** del ciclista
3. Usa **ropa ajustada** (culotte + maillot)
4. Buena **iluminación**, fondo limpio
5. Pedalea **15-20 segundos** a cadencia normal (80-90 rpm)
6. Manos en las manetas, posición natural

## API

### `GET /health`
Health check.

### `POST /analyze?discipline=road`
Sube un video y recibe el análisis.

**Parámetros:**
- `video`: archivo de video (multipart)
- `discipline`: `road` | `mtb` | `tt`

**Respuesta:**
```json
{
  "contact_points": {
    "saddle_knee_angle": 145.2,
    "saddle_hip_angle": 74.1,
    "hands_elbow_angle": 158.3,
    "hands_back_angle": 41.0,
    "feet_ankle_angle": 105.7
  },
  "recommendations": [
    {
      "contact_point": "saddle",
      "metric": "saddle_knee_angle",
      "value": 145.2,
      "ideal_range": [140.0, 150.0],
      "severity": "ok",
      "adjustment": "saddle",
      "message": "Correcto"
    }
  ],
  "frames_analyzed": 312,
  "annotated_frame": "<base64 JPG>"
}
```

## Stack

- **Backend:** Python, FastAPI, NumPy
- **Visión:** MediaPipe Pose, OpenCV
- **Frontend:** HTML/CSS/JS vanilla (single page)

## Estructura

```
bikefit/
├── app/
│   ├── main.py              # API FastAPI
│   ├── models.py            # Modelos de datos
│   ├── engine/
│   │   ├── angles.py        # Cálculo de ángulos
│   │   ├── rules.py         # Sistema experto biomecánico
│   │   └── video.py         # Procesador de video + frame anotado
│   └── static/
│       └── index.html       # Frontend
└── requirements.txt
```

## Limitaciones del MVP

- Solo analiza el lado derecho
- Requiere video lateral (2D, no 3D)
- Funciona mejor en rodillo indoor (posición estable, sin viento)
- La ropa suelta puede afectar la detección de articulaciones
