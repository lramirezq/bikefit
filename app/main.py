"""API BikeFit: endpoint para analizar video de ciclista."""

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.engine.video import process_video
from app.models import Discipline, FitResult

app = FastAPI(title="BikeFit API", version="0.1.0")

STATIC_DIR = Path(__file__).parent / "static"


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=FitResult)
async def analyze_video(
    video: UploadFile = File(...),
    discipline: Discipline = Query(default=Discipline.ROAD),
):
    """Sube un video lateral del ciclista y recibe análisis de bikefit."""
    suffix = Path(video.filename or "video.mp4").suffix
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await video.read())
        tmp_path = tmp.name

    result = process_video(tmp_path, discipline)
    Path(tmp_path).unlink(missing_ok=True)
    return result
