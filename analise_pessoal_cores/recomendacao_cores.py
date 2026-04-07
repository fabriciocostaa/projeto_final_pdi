from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFont


PALETAS = {
    "spring": {
        "nome": "Tom Quente de Primavera",
        "fundo": "#FFF8F0",
        "texto": "#7A3B00",
        "cores": [
            "#F4A460", "#FF7F50", "#FFD700", "#FF6347",
            "#FFA07A", "#FFB347", "#FFDAB9", "#FF8C69",
            "#E9967A", "#FFC87C", "#FF9966", "#F08030",
            "#FFCC44", "#FF704D", "#FFD580", "#F4C430",
            "#E8722A", "#FFB347", "#FF7733", "#FFA040",
        ],
    },
    "fall": {
        "nome": "Tom Quente de Outono",
        "fundo": "#FDF5E6",
        "texto": "#4A2000",
        "cores": [
            "#8B4513", "#D2691E", "#CD853F", "#B8860B",
            "#A0522D", "#CC7722", "#556B2F", "#704214",
            "#8B6914", "#C68642", "#9B4A1F", "#6B3A2A",
            "#A67C52", "#7C5C3E", "#5C4033", "#3E2723",
            "#B5651D", "#8D5524", "#D4A017", "#7A5230",
        ],
    },
    "summer": {
        "nome": "Tom Fresco de Verao",
        "fundo": "#F5F5FA",
        "texto": "#2E4060",
        "cores": [
            "#B0C4DE", "#DDA0DD", "#E6E6FA", "#C0C0C0",
            "#ADD8E6", "#D8BFD8", "#B09AB0", "#A9A9A9",
            "#9BB5C8", "#C8A8C8", "#8FA8BE", "#D4B0D4",
            "#B8A0C8", "#A0B8D0", "#C0A8B8", "#9898B8",
            "#A8B8C8", "#C8B0C0", "#B0A8C0", "#A0A8B8",
        ],
    },
    "winter": {
        "nome": "Tom Frio de Inverno",
        "fundo": "#F0F0F8",
        "texto": "#0A0A2A",
        "cores": [
            "#000080", "#DC143C", "#4B0082", "#FFFFFF",
            "#000000", "#008080", "#800020", "#191970",
            "#0000CD", "#C0392B", "#6A0DAD", "#E8E8E8",
            "#003366", "#CC0033", "#330066", "#F0F0F0",
            "#001F5B", "#990000", "#2C0054", "#D0D0D0",
        ],
    },
}

_ALIAS = {
    "Tom quente de primavera": "spring",
    "Tom quente de outono": "fall",
    "Tom fresco de verao": "summer",
    "Tom legal de inverno": "winter",
    "spring": "spring",
    "fall": "fall",
    "summer": "summer",
    "winter": "winter",
}


def _hex_to_rgb(hex_cor: str) -> tuple[int, int, int]:
    hex_value = hex_cor.lstrip("#")
    return tuple(int(hex_value[i:i + 2], 16) for i in (0, 2, 4))


def _normalizar_tom(tom: str) -> str:
    chave = _ALIAS.get(tom.strip().lower())
    if chave is None:
        raise ValueError(f"Tom '{tom}' nao reconhecido.")
    return chave


def _foto_circular(foto_path: str, diametro: int) -> Image.Image:
    foto = Image.open(foto_path).convert("RGBA")

    width, height = foto.size
    lado = min(width, height)
    left = (width - lado) // 2
    top = (height - lado) // 2
    foto = foto.crop((left, top, left + lado, top + lado))
    foto = foto.resize((diametro, diametro), Image.LANCZOS)

    mascara = Image.new("L", (diametro, diametro), 0)
    ImageDraw.Draw(mascara).ellipse([0, 0, diametro, diametro], fill=255)
    foto.putalpha(mascara)
    return foto


def gerar_paleta(tom: str, foto_path: str, caminho_saida: str | None = None) -> str:
    chave = _normalizar_tom(tom)
    paleta = PALETAS[chave]
    cores = paleta["cores"]
    total_cores = len(cores)

    width = height = 600
    center_x = center_y = width // 2
    raio_externo = 260
    raio_interno = 115
    borda_branca = 8

    bg_rgb = _hex_to_rgb(paleta["fundo"])
    canvas = Image.new("RGBA", (width, height), bg_rgb + (255,))
    draw = ImageDraw.Draw(canvas)

    angulo_fatia = 360 / total_cores
    for i, cor in enumerate(cores):
        start = i * angulo_fatia - 90
        end = start + angulo_fatia + 0.5
        bbox = [
            center_x - raio_externo,
            center_y - raio_externo,
            center_x + raio_externo,
            center_y + raio_externo,
        ]
        draw.pieslice(bbox, start=start, end=end, fill=_hex_to_rgb(cor) + (255,))

    raio_borda = raio_interno + borda_branca
    draw.ellipse(
        [center_x - raio_borda, center_y - raio_borda, center_x + raio_borda, center_y + raio_borda],
        fill=(255, 255, 255, 255),
    )

    foto_diametro = raio_interno * 2
    foto_circular = _foto_circular(foto_path, foto_diametro)
    posicao = (center_x - raio_interno, center_y - raio_interno)
    canvas.paste(foto_circular, posicao, mask=foto_circular)

    label = paleta["nome"]
    fonte_size = 22
    try:
        fonte = ImageFont.truetype("arial.ttf", fonte_size)
    except OSError:
        fonte = ImageFont.load_default()

    padding_x = 18
    padding_y = 14
    bbox_texto = draw.textbbox((0, 0), label, font=fonte)
    text_width = bbox_texto[2] - bbox_texto[0]
    text_height = bbox_texto[3] - bbox_texto[1]

    rect_x0 = 20
    rect_y0 = height - text_height - padding_y * 2 - 20
    rect_x1 = rect_x0 + text_width + padding_x * 2
    rect_y1 = height - 20

    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rounded_rectangle([rect_x0, rect_y0, rect_x1, rect_y1], radius=8, fill=(0, 0, 0, 140))
    canvas = Image.alpha_composite(canvas, overlay)

    final_draw = ImageDraw.Draw(canvas)
    final_draw.text((rect_x0 + padding_x, rect_y0 + padding_y), label, font=fonte, fill=(255, 255, 255, 255))

    canvas_rgb = canvas.convert("RGB")

    if caminho_saida is None:
        caminho_saida = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            f"paleta_{chave}.png",
        )

    canvas_rgb.save(caminho_saida, dpi=(150, 150))
    return caminho_saida
