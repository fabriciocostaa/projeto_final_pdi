from __future__ import annotations

import argparse
from pathlib import Path

from .cores_pessoais import analysis
from .recomendacao_cores import gerar_paleta


def main() -> None:
    parser = argparse.ArgumentParser(description="Analise de coloracao pessoal.")
    parser.add_argument("--image", required=False, help="Caminho para uma imagem .jpg ou .png.")
    parser.add_argument("--dir", required=False, help="Diretorio com varias imagens.")
    args = parser.parse_args()

    if args.image:
        imgpath = Path(args.image)
        tone = analysis(str(imgpath))
        output_path = imgpath.parent / "resultado.jpg"
        gerar_paleta(tone, str(imgpath), str(output_path))
        return

    if args.dir:
        dirpath = Path(args.dir)
        for imgpath in dirpath.iterdir():
            if imgpath.is_file():
                analysis(str(imgpath))
        return

    parser.error("Informe --image ou --dir.")


if __name__ == "__main__":
    main()
