from __future__ import annotations

import cv2
import numpy as np
from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor, sRGBColor


# Valores de referência reais do X-Rite ColorChecker Classic (24 patches) em sRGB [0-255]
# Linha 1: tons de pele e natureza | Linha 2: cores primárias/secundárias
# Linha 3: cores saturadas        | Linha 4: escala de cinza
REFERENCE_PATCHES_RGB: list[tuple[int, int, int]] = [
    # Linha 1
    (115, 82,  68),   # 1  Dark Skin
    (194, 150, 130),  # 2  Light Skin
    (98,  122, 157),  # 3  Blue Sky
    (87,  108, 67),   # 4  Foliage
    (133, 128, 177),  # 5  Blue Flower
    (103, 189, 170),  # 6  Bluish Green
    # Linha 2
    (214, 126, 44),   # 7  Orange
    (80,  91,  166),  # 8  Purplish Blue
    (193, 90,  99),   # 9  Moderate Red
    (94,  60,  108),  # 10 Purple
    (157, 188, 64),   # 11 Yellow Green
    (224, 163, 46),   # 12 Orange Yellow
    # Linha 3
    (56,  61,  150),  # 13 Blue
    (70,  148, 73),   # 14 Green
    (175, 54,  60),   # 15 Red
    (231, 199, 31),   # 16 Yellow
    (187, 86,  149),  # 17 Magenta
    (8,   133, 161),  # 18 Cyan
    # Linha 4 — escala de cinza
    (243, 243, 243),  # 19 White
    (200, 200, 200),  # 20 Neutral 8
    (160, 160, 160),  # 21 Neutral 6.5
    (122, 122, 121),  # 22 Neutral 5
    (85,  85,  85),   # 23 Neutral 3.5
    (52,  52,  52),   # 24 Black
]

PATCH_NAMES = [
    "Dark Skin", "Light Skin", "Blue Sky", "Foliage", "Blue Flower", "Bluish Green",
    "Orange", "Purplish Blue", "Moderate Red", "Purple", "Yellow Green", "Orange Yellow",
    "Blue", "Green", "Red", "Yellow", "Magenta", "Cyan",
    "White", "Neutral 8", "Neutral 6.5", "Neutral 5", "Neutral 3.5", "Black",
]


def _rgb_to_lab(r: int, g: int, b: int) -> tuple[float, float, float]:
    """Converte RGB [0-255] para Lab via colormath."""
    rgb = sRGBColor(r, g, b, is_upscaled=True)
    lab = convert_color(rgb, LabColor, through_rgb_type=sRGBColor)
    return lab.lab_l, lab.lab_a, lab.lab_b


def _delta_e(lab1: tuple[float, float, float], lab2: tuple[float, float, float]) -> float:
    """Calcula Delta E CIE76 entre dois valores Lab."""
    return float(np.sqrt(sum((a - b) ** 2 for a, b in zip(lab1, lab2))))


def detectar_patches(image_path: str, grid_rows: int = 4, grid_cols: int = 6) -> list[tuple[int, int, int]]:
    """
    Detecta automaticamente os 24 patches do color checker na imagem.
    Assume que o color checker ocupa a maior parte da imagem ou foi recortado.
    Divide em grid 4x6 e extrai a cor média do centro de cada célula.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Nao foi possivel carregar a imagem: {image_path}")

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w = img_rgb.shape[:2]

    cell_h = h // grid_rows
    cell_w = w // grid_cols

    # Margem interna para evitar bordas entre patches (20% de cada lado)
    margin_h = int(cell_h * 0.20)
    margin_w = int(cell_w * 0.20)

    patches: list[tuple[int, int, int]] = []

    for row in range(grid_rows):
        for col in range(grid_cols):
            y0 = row * cell_h + margin_h
            y1 = (row + 1) * cell_h - margin_h
            x0 = col * cell_w + margin_w
            x1 = (col + 1) * cell_w - margin_w

            region = img_rgb[y0:y1, x0:x1]
            mean_color = region.mean(axis=(0, 1))
            patches.append((int(mean_color[0]), int(mean_color[1]), int(mean_color[2])))

    return patches


def calcular_metricas(
    patches_medidos: list[tuple[int, int, int]],
    patches_referencia: list[tuple[int, int, int]] = REFERENCE_PATCHES_RGB,
) -> dict[str, object]:
    """
    Compara os patches medidos com os valores de referência.
    Retorna Delta E por patch, média, máximo e classificação de acurácia.
    """
    if len(patches_medidos) != len(patches_referencia):
        raise ValueError(
            f"Numero de patches medidos ({len(patches_medidos)}) "
            f"diferente do esperado ({len(patches_referencia)})."
        )

    delta_es: list[float] = []
    detalhes: list[dict] = []

    for i, (medido, referencia) in enumerate(zip(patches_medidos, patches_referencia)):
        lab_medido = _rgb_to_lab(*medido)
        lab_referencia = _rgb_to_lab(*referencia)
        de = _delta_e(lab_medido, lab_referencia)
        delta_es.append(de)

        detalhes.append({
            "patch": i + 1,
            "nome": PATCH_NAMES[i],
            "rgb_medido": medido,
            "rgb_referencia": referencia,
            "delta_e": round(de, 2),
        })

    media = float(np.mean(delta_es))
    maximo = float(np.max(delta_es))

    # Classificação baseada em limiares perceptuais do Delta E
    if media < 1.0:
        classificacao = "Excelente — diferença imperceptível ao olho humano"
    elif media < 2.0:
        classificacao = "Bom — diferença perceptível apenas por observadores treinados"
    elif media < 4.0:
        classificacao = "Aceitável — diferença perceptível mas tolerável"
    elif media < 8.0:
        classificacao = "Ruim — diferença claramente visível"
    else:
        classificacao = "Crítico — cores com desvio severo"

    return {
        "delta_e_medio": round(media, 2),
        "delta_e_maximo": round(maximo, 2),
        "classificacao": classificacao,
        "total_patches": len(patches_medidos),
        "patches_aceitaveis": sum(1 for de in delta_es if de < 4.0),
        "detalhes": detalhes,
    }

def gerar_ccm(patches_medidos, patches_referencia):
    # Converte listas de tuplas para arrays numpy e normaliza
    medidos = np.array(patches_medidos, dtype=np.float32) / 255.0
    referencia = np.array(patches_referencia, dtype=np.float32) / 255.0
    # Resolve Medidos * CCM = Referencia
    ccm, _, _, _ = np.linalg.lstsq(medidos, referencia, rcond=None)
    return ccm