from __future__ import annotations

import base64
from pathlib import Path


MODULE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = MODULE_DIR.parent
STATIC_DIR = PROJECT_ROOT / "static"
DEFAULT_RESULT_IMAGE_RELATIVE_PATH = "images/cool-summer.8128e21d.png"
DEFAULT_RESULT_IMAGE_PATH = STATIC_DIR / DEFAULT_RESULT_IMAGE_RELATIVE_PATH


def encode_image_base64(image_path: str | Path) -> str:
    resolved_path = Path(image_path)
    if not resolved_path.exists():
        raise FileNotFoundError(f"Nao foi possivel localizar a imagem: {resolved_path}")
    return base64.b64encode(resolved_path.read_bytes()).decode("utf-8")


def build_default_result_image_payload() -> dict[str, str]:
    image_base64 = encode_image_base64(DEFAULT_RESULT_IMAGE_PATH)
    return {
        "url": f"/static/{DEFAULT_RESULT_IMAGE_RELATIVE_PATH}",
        "base64": image_base64,
        "data_url": f"data:image/png;base64,{image_base64}",
    }
