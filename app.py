from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from analise_pessoal_cores import analysis_details, capturar_imagem


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
CAPTURED_IMAGE_PATH = STATIC_DIR / "images" / "sua_foto.jpg"

class AnaliseRequest(BaseModel):
    capturar_webcam: bool = True

app = FastAPI(
    title="Color Match API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "API de colorimetria online."}


@app.post("/api/analise")
def iniciar_analise() -> dict[str, object]:  # payload: AnaliseRequest
    try:
        capturar_imagem(CAPTURED_IMAGE_PATH)
        resultado = analysis_details(str(CAPTURED_IMAGE_PATH))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "status": "sucesso",
        "resultado": {
            "tom_principal": resultado["estacao"],
            "tom_detectado": resultado["tom"],
            "informacoes_estacao": resultado["descricao_estacao"],
            "criterios_decisao": resultado["criterios"],
            "imagem_exibicao_base64": resultado["imagem_resultado"]["base64"],
        },
    }


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
