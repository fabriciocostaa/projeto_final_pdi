from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from analise_pessoal_cores import analysis_details, save_base64_as_jpg, encode_image_base64, gerar_paleta
from analise_pessoal_cores import check_cores
from analise_pessoal_cores import DetectFace, capturar_imagem
from analise_pessoal_cores.utils import img_to_base64

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
CAPTURED_IMAGE_PATH = STATIC_DIR / "images" / "sua_foto.jpg"
UPLOADED_IMAGE_PATH = STATIC_DIR / "images" / "imagem_carregada.jpg"
RESULT_IMAGE_PATH = STATIC_DIR / "images" / "imagem_resultado.jpg"
IMAGE_CHECK_PATH = STATIC_DIR / "images" / "correcao_cores.jpg"

MATRIZ_CALIBRACAO = None 

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
        capturar_imagem()

        if MATRIZ_CALIBRACAO is not None:
            check_cores.corrigir_imagem(CAPTURED_IMAGE_PATH, MATRIZ_CALIBRACAO) #usando o colorchecker

        detect = DetectFace(str(CAPTURED_IMAGE_PATH))
        resultado = analysis_details(str(CAPTURED_IMAGE_PATH), detect=detect)
        gerar_paleta(resultado["tom"], str(CAPTURED_IMAGE_PATH), str(RESULT_IMAGE_PATH))
    except FileNotFoundError as exc:
        print(f"Erro FileNotFoundError: {exc}")
        raise HTTPException(status_code=404, detail="Imagem não encontrada.") from exc
    except Exception as exc:
        print(f"Erro Exception: {exc}")
        raise HTTPException(status_code=400, detail="Erro ao processar a imagem, tente uma imagem mais iluminada !") from exc

    return {
        "status": "sucesso",

        "etapas": {
            "gaussiano": img_to_base64(detect.gaussian_img),
            "landmarks": img_to_base64(detect.landmarks_img),
            "segmentacao": img_to_base64(detect.segmentacao_img)
        },

        "resultado": {
            "tom_principal": resultado["estacao"],
            "tom_detectado": resultado["tom"],
            "informacoes_estacao": resultado["descricao_estacao"],
            "criterios_decisao": resultado["criterios"],
            "imagem_exibicao_base64": encode_image_base64(RESULT_IMAGE_PATH),
        },
    }


@app.post("/api/analise_upload")
def iniciar_analise_upload(payload: AnaliseUploadRequest) -> dict[str, object]:
    try:
        # salva imagem enviada
        save_base64_as_jpg(payload.imagem_base64, UPLOADED_IMAGE_PATH)

        if MATRIZ_CALIBRACAO is not None:
            check_cores.corrigir_imagem(UPLOADED_IMAGE_PATH, MATRIZ_CALIBRACAO) #usando o colorchecker

        detect = DetectFace(str(UPLOADED_IMAGE_PATH))

        # análise original continua igual
        resultado = analysis_details(str(UPLOADED_IMAGE_PATH), detect= detect)
        gerar_paleta(resultado["tom"], str(UPLOADED_IMAGE_PATH), str(RESULT_IMAGE_PATH))

    except FileNotFoundError as exc:
        print(f"ERRO FileNotFoundError: {exc}")
        raise HTTPException(status_code=404, detail="Imagem não encontrada.") from exc
    except Exception as exc:
        print(f"ERRO Exception: {exc}")
        raise HTTPException(status_code=400, detail="Erro ao processar a imagem, tente uma imagem mais iluminada !") from exc

    return {
        "status": "sucesso",

        "etapas": {
            "gaussiano": img_to_base64(detect.gaussian_img),
            "landmarks": img_to_base64(detect.landmarks_img),
            "segmentacao": img_to_base64(detect.segmentacao_img)
        },

        "resultado": {
            "tom_principal": resultado["estacao"],
            "tom_detectado": resultado["tom"],
            "informacoes_estacao": resultado["descricao_estacao"],
            "criterios_decisao": resultado["criterios"],
            "imagem_exibicao_base64": encode_image_base64(RESULT_IMAGE_PATH),
        },
    }

@app.post("/api/check_cores")
def calibracao() -> dict[str, object]:
    global MATRIZ_CALIBRACAO
    try:
        capturar_imagem(IMAGE_CHECK_PATH)
        # 1. Detecta os patches
        patches_lidos = check_cores.detectar_patches(str(IMAGE_CHECK_PATH))
        # 2. Calcula métricas para o log/front
        metricas = check_cores.calcular_metricas(patches_lidos)
        # 3. GERA E SALVA A MATRIZ
        MATRIZ_CALIBRACAO = check_cores.gerar_ccm(patches_lidos, check_cores.REFERENCE_PATCHES_RGB)
        print(MATRIZ_CALIBRACAO)
    except FileNotFoundError as exc:
        print(f"ERRO FileNotFoundError: {exc}")
        raise HTTPException(status_code=404, detail="Imagem não encontrada.") from exc
    except Exception as exc:
        print(f"ERRO Exception: {exc}")
        raise HTTPException(status_code=400, detail="Erro ao processar calibração.") from exc
    
    return {"status": "sucesso", "metricas": metricas, "calibrado": True}


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
