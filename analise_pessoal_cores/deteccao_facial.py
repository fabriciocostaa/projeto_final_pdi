from __future__ import annotations

from pathlib import Path

import cv2
import dlib
import numpy as np
from imutils import face_utils


MODULE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = MODULE_DIR.parent
DEFAULT_LANDMARK_PATH = PROJECT_ROOT / "shape_predictor_68_face_landmarks.dat"
DEFAULT_CAPTURE_PATH = PROJECT_ROOT / "static" / "images" / "sua_foto.jpg"


def preparar_caminho_imagem(
    path_img: str | Path | None = None,
    output_path: str | Path = DEFAULT_CAPTURE_PATH,
) -> Path:
    if path_img is not None:
        resolved_path = Path(path_img)
        if not resolved_path.exists():
            raise FileNotFoundError(f"Nao foi possivel localizar a imagem: {resolved_path}")
        return resolved_path

    capturar_imagem(output_path)
    return Path(output_path)


def capturar_imagem(output_path: str | Path = DEFAULT_CAPTURE_PATH) -> None:
    cap = cv2.VideoCapture(0)

    output_path = Path(output_path)

    if not cap.isOpened():
        raise RuntimeError("Nao foi possivel abrir a camera.")

    while True:
        ret, frame = cap.read()
        if not ret:
            raise RuntimeError("Nao foi possivel capturar frame da camera.")

        cv2.imshow("Imagem", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):
            cv2.imwrite(str(output_path), frame)
        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)


class DetectFace:
    def __init__(self, image: str | Path, predictor_path: str | Path = DEFAULT_LANDMARK_PATH,ccm: np.ndarray | None = None, white_patch_rgb: np.ndarray | None = None) -> None:
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(str(predictor_path))

        img_raw = cv2.imread(str(image))
        if img_raw is None:
            raise FileNotFoundError(f"Nao foi possivel carregar a imagem: {image}")
        
        # 1. CORREÇÃO DE PONTO BRANCO (Sempre na imagem nítida)
        if white_patch_rgb is not None:
            img_raw = self._corrigir_ponto_branco(img_raw, white_patch_rgb)
            print(f"array de ponto branco: {white_patch_rgb}")

        # 2. APLICAR MATRIZ CCM (Sempre na imagem nítida)
        if ccm is not None:
            img_raw = self._aplicar_ccm(img_raw, ccm)

        # Agora guardamos a imagem final calibrada e nítida
        self.original = img_raw

        # 3. FILTRO GAUSSIANO (Criado a partir da imagem já calibrada)
        # self.img é usada para extrair as cores das partes do rosto
        self.img = cv2.GaussianBlur(self.original, (5, 5), 0)

        self.right_eyebrow: np.ndarray | list[object] = []
        self.left_eyebrow: np.ndarray | list[object] = []
        self.right_eye: np.ndarray | list[object] = []
        self.left_eye: np.ndarray | list[object] = []
        self.left_cheek: np.ndarray | list[object] = []
        self.right_cheek: np.ndarray | list[object] = []

        self.detect_face_part()

    def _corrigir_ponto_branco(self, img_bgr: np.ndarray, white_patch_rgb: np.ndarray) -> np.ndarray:
        # Converte para float32 [0, 1]
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        
        # Evita divisão por zero e calcula ganhos
        source_wp = np.maximum(white_patch_rgb / 255.0, 1e-5)
        gains = 1.0 / source_wp
        
        # Aplica e clipa
        corrected = np.clip(img_rgb * gains, 0, 1)
        
        # Volta para BGR 8-bit
        corrected_8bit = (corrected * 255).astype(np.uint8)
        return cv2.cvtColor(corrected_8bit, cv2.COLOR_RGB2BGR)

    def _aplicar_ccm(self, img_bgr: np.ndarray, ccm: np.ndarray) -> np.ndarray:
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        img_corrigida = np.clip(img_rgb @ ccm, 0, 1)
        res = (img_corrigida * 255).astype(np.uint8)
        return cv2.cvtColor(res, cv2.COLOR_RGB2BGR)

    def detect_face_part(self) -> None:
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        rects = self.detector(gray, 1)

        if len(rects) == 0:
            raise Exception("Nao foi possivel detectar um rosto na imagem. Tente uma foto mais clara.")

        rect = rects[0]
        shape = self.predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        face_parts = []
        for _, (i, j) in face_utils.FACIAL_LANDMARKS_IDXS.items():
            face_parts.append(shape[i:j])
        face_parts = face_parts[1:5]

        self.gaussian_img = self.img.copy()

        self.landmarks_img = self.original.copy()
        for (x, y) in shape:
            cv2.circle(self.landmarks_img, (x, y), 2, (0, 255, 0), -1)    
        
        idxs = dict(face_utils.FACIAL_LANDMARKS_IDXS)
        self.right_eyebrow = self.extract_face_part(shape[idxs["right_eyebrow"][0]:idxs["right_eyebrow"][1]])
        self.left_eyebrow  = self.extract_face_part(shape[idxs["left_eyebrow"][0]:idxs["left_eyebrow"][1]])
        self.right_eye     = self.extract_face_part(shape[idxs["right_eye"][0]:idxs["right_eye"][1]])
        self.left_eye      = self.extract_face_part(shape[idxs["left_eye"][0]:idxs["left_eye"][1]])
        self.left_cheek = self.img[shape[29][1]:shape[33][1], shape[4][0]:shape[48][0]]
        self.right_cheek = self.img[shape[29][1]:shape[33][1], shape[54][0]:shape[12][0]]

        # imagem das regiões segmentadas destacadas
        self.segmentacao_img = self.gaussian_img.copy()
        regioes = [
            (shape[29][1], shape[33][1], shape[4][0],  shape[48][0]),   # bochecha esquerda
            (shape[29][1], shape[33][1], shape[54][0], shape[12][0]),   # bochecha direita
        ]
        for (y0, y1, x0, x1) in regioes:
            cv2.rectangle(self.segmentacao_img, (x0, y0), (x1, y1), (255, 165, 0), 2)

        for points in [face_parts[0], face_parts[1], face_parts[2], face_parts[3]]:
            hull = cv2.convexHull(points)
            cv2.polylines(self.segmentacao_img, [hull], True, (255, 165, 0), 2)

    def extract_face_part(self, face_part_points: np.ndarray) -> np.ndarray:
        x, y, w, h = cv2.boundingRect(face_part_points)
    
        # .copy() evita que modificações no crop afetem self.img original
        crop = self.img[y:y + h, x:x + w].copy()
        
        # ajusta os pontos dos landmarks para coordenadas locais do recorte
        adj_points = np.array([np.array([p[0] - x, p[1] - y]) for p in face_part_points])

        # cria máscara binária zerada do mesmo tamanho do recorte
        # fillConvexPoly preenche o interior do contorno dos landmarks com 1
        mask = np.zeros((crop.shape[0], crop.shape[1]), dtype=np.uint8)
        cv2.fillConvexPoly(mask, adj_points, 1)

        # MORPH_CLOSE = dilatação seguida de erosão
        # fecha buracos internos na máscara causados por gaps entre os landmarks
        # exemplo: pixels não cobertos pelo fillConvexPoly dentro da sobrancelha
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # MORPH_OPEN = erosão seguida de dilatação
        # remove pixels espúrios nas bordas da máscara gerados pelo fillConvexPoly
        # evita que pixels de pele ao redor da região contaminem a extração de cor
        # a ordem CLOSE → OPEN é intencional: primeiro fecha buracos, depois limpa bordas
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # converte para bool e pinta pixels fora da máscara de azul [255, 0, 0]
        # o azul é filtrado depois no color_extract.py pelo color_filter do get_histogram
        mask = mask.astype(bool)
        crop[np.logical_not(mask)] = [255, 0, 0]
        return crop
