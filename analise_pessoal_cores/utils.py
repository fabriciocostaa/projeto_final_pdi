from __future__ import annotations

import base64
import io
from pathlib import Path
from PIL import Image


MODULE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = MODULE_DIR.parent
STATIC_DIR = PROJECT_ROOT / "static"
DEFAULT_RESULT_IMAGE_RELATIVE_PATH = "images/imagem_resultado.jpg"
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


def save_base64_as_jpg(image_base64: str, output_path: str | Path) -> Path:
    base64_content = image_base64.strip()
    if "," in base64_content:
        base64_content = base64_content.split(",", 1)[1]

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    image_bytes = base64.b64decode(base64_content)
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image.save(output, format="JPEG")

    return output
