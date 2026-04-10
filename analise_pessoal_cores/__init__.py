from __future__ import annotations

from importlib import import_module

__all__ = [
    "DetectFace",
    "DominantColors",
    "analysis",
    "analysis_details",
    "build_default_result_image_payload",
    "capturar_imagem",
    "encode_image_base64",
    "gerar_paleta",
    "is_warm",
    "is_spr",
    "is_smr",
    "preparar_caminho_imagem",
    "save_base64_as_jpg",
]

_EXPORT_MAP = {
    "is_warm": (".analise_tom", "is_warm"),
    "is_spr": (".analise_tom", "is_spr"),
    "is_smr": (".analise_tom", "is_smr"),
    "DominantColors": (".color_extract", "DominantColors"),
    "analysis": (".cores_pessoais", "analysis"),
    "analysis_details": (".cores_pessoais", "analysis_details"),
    "DetectFace": (".deteccao_facial", "DetectFace"),
    "capturar_imagem": (".deteccao_facial", "capturar_imagem"),
    "preparar_caminho_imagem": (".deteccao_facial", "preparar_caminho_imagem"),
    "build_default_result_image_payload": (".utils", "build_default_result_image_payload"),
    "encode_image_base64": (".utils", "encode_image_base64"),
    "save_base64_as_jpg": (".utils", "save_base64_as_jpg"),
    "gerar_paleta": (".recomendacao_cores", "gerar_paleta"),
}


def __getattr__(name: str):
    if name not in _EXPORT_MAP:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name, attr_name = _EXPORT_MAP[name]
    module = import_module(module_name, __name__)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value
