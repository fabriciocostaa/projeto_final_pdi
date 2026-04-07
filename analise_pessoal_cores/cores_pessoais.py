from __future__ import annotations

import os

import numpy as np
from colormath.color_conversions import convert_color
from colormath.color_objects import HSVColor, LabColor, sRGBColor

from . import analise_tom
from .color_extract import DominantColors
from .deteccao_facial import DetectFace


def analysis(imgpath: str) -> str:
    df = DetectFace(imgpath)
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

    if analise_tom.is_warm(lab_b_values, lab_weight):
        if analise_tom.is_spr(hsv_s_values, hsv_weight):
            tone = "tom quente de primavera(spring)"
        else:
            tone = "tom quente de outono(fall)"
    else:
        if analise_tom.is_smr(hsv_s_values, hsv_weight):
            tone = "tom fresco de verao(summer)"
        else:
            tone = "tom legal de inverno(winter)"

    print(f"A coloracao pessoal de {os.path.basename(imgpath)} e {tone}.")
    return tone
