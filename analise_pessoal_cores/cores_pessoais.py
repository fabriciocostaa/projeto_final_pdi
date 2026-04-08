from __future__ import annotations

import os

import numpy as np
from colormath.color_conversions import convert_color
from colormath.color_objects import HSVColor, LabColor, sRGBColor

from . import analise_tom
from .color_extract import DominantColors
from .deteccao_facial import DetectFace, preparar_caminho_imagem
from .utils import build_default_result_image_payload


SEASON_DETAILS = {
    "spring": {
        "estacao": "Primavera",
        "descricao": "Perfil de tons quentes, vivos e luminosos, normalmente favorecido por cores claras e energicas.",
    },
    "summer": {
        "estacao": "Verão",
        "descricao": "Perfil de tons frios e suaves, geralmente harmonizado com cores delicadas, acinzentadas e elegantes.",
    },
    "fall": {
        "estacao": "Outono",
        "descricao": "Perfil de tons quentes e terrosos, com melhor resposta a cores profundas, naturais e acolhedoras.",
    },
    "winter": {
        "estacao": "Inverno",
        "descricao": "Perfil de tons frios e intensos, valorizado por contrastes altos e cores nitidas e marcantes.",
    },
}

TONE_TO_SEASON = {
    "Tom quente de primavera": "spring",
    "Tom quente de outono": "fall",
    "Tom fresco de verao": "summer",
    "Tom fresco de verão": "summer",
    "Tom legal de inverno": "winter",
}


def analysis_details(imgpath: str | None = None) -> dict[str, object]:
    resolved_imgpath = preparar_caminho_imagem(imgpath)
    df = DetectFace(resolved_imgpath)
    face_parts = [
        df.left_cheek,
        df.right_cheek,
        df.left_eyebrow,
        df.right_eyebrow,
        df.left_eye,
        df.right_eye,
    ]

    extracted_colors = []
    clusters = 4

    for face_part in face_parts:
        dc = DominantColors(face_part, clusters)
        face_part_colors, _ = dc.get_histogram()
        if not face_part_colors:
            raise ValueError("Nao foi possivel extrair uma cor dominante da imagem.")
        extracted_colors.append(np.array(face_part_colors[0]))

    cheek = np.mean([extracted_colors[0], extracted_colors[1]], axis=0)
    eyebrow = np.mean([extracted_colors[2], extracted_colors[3]], axis=0)
    eye = np.mean([extracted_colors[4], extracted_colors[5]], axis=0)

    lab_b_values: list[float] = []
    hsv_s_values: list[float] = []

    for color in [cheek, eyebrow, eye]:
        rgb = sRGBColor(color[0], color[1], color[2], is_upscaled=True)
        lab = convert_color(rgb, LabColor, through_rgb_type=sRGBColor)
        hsv = convert_color(rgb, HSVColor, through_rgb_type=sRGBColor)
        lab_b_values.append(float(format(lab.lab_b, ".2f")))
        hsv_s_values.append(float(format(hsv.hsv_s, ".2f")) * 100)

    lab_weight = [30, 20, 5]
    hsv_weight = [10, 1, 1]

    subtom = "quente" if analise_tom.is_warm(lab_b_values, lab_weight) else "frio"

    if subtom == "quente":
        if analise_tom.is_spr(hsv_s_values, hsv_weight):
            tone = "Tom quente de primavera"
        else:
            tone = "Tom quente de outono"
    else:
        if analise_tom.is_smr(hsv_s_values, hsv_weight):
            tone = "Tom fresco de verão"
        else:
            tone = "Tom legal de inverno"

    season_key = TONE_TO_SEASON[tone]
    season_info = SEASON_DETAILS[season_key]

    result = {
        "imagem_analisada": os.path.basename(str(resolved_imgpath)),
        "tom": tone,
        "estacao": season_info["estacao"],
        "estacao_chave": season_key,
        "descricao_estacao": season_info["descricao"],
        "imagem_resultado": build_default_result_image_payload(),
        "criterios": {
            "partes_analisadas": ["pele", "sobrancelhas", "olhos"],
            "metodo": [
                "Comparação de temperatura entre referencias quentes e frias usando o canal Lab b.",
                "Comparação de saturacao em HSV para diferenciar primavera e outono.",
                "Comparação de saturacao em HSV para diferenciar verão e inverno.",
            ],
            "subtom_identificado": subtom,
        },
    }

    print(f"A coloracao pessoal de {os.path.basename(str(resolved_imgpath))} e {tone}.")
    return result
