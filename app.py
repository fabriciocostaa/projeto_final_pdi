from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from analise_pessoal_cores import analysis_details, save_base64_as_jpg


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
CAPTURED_IMAGE_PATH = STATIC_DIR / "images" / "sua_foto.jpg"
UPLOADED_IMAGE_PATH = STATIC_DIR / "images" / "imagem_carregada.jpg"

class AnaliseRequest(BaseModel):
    capturar_webcam: bool = True


class AnaliseUploadRequest(BaseModel):
    imagem_base64: str

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

@app.get("/health")
def read_root() -> dict[str, str]:
    return {"message": "API de colorimetria online."}


@app.get("/", include_in_schema=False)
def read_root() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/analise")
def iniciar_analise() -> dict[str, object]:  # payload: AnaliseRequest
    try:
        resultado = analysis_details()
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


@app.post("/api/analise_upload")
def iniciar_analise_upload(payload: AnaliseUploadRequest) -> dict[str, object]:
    try:
        save_base64_as_jpg(payload.imagem_base64, UPLOADED_IMAGE_PATH)
        resultado = analysis_details(str(UPLOADED_IMAGE_PATH))
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
