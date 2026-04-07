from __future__ import annotations

from importlib import import_module

__all__ = [
    "DetectFace",
    "DominantColors",
    "analysis",
    "analysis_details",
    "capturar_imagem",
    "gerar_paleta",
    "is_warm",
    "is_spr",
    "is_smr",
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
