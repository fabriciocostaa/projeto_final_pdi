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
    print("Pressione [s] para salvar as imagens ou [q] para sair.")

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
    def __init__(self, image: str | Path, predictor_path: str | Path = DEFAULT_LANDMARK_PATH) -> None:
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(str(predictor_path))

        self.img = cv2.imread(str(image))
        if self.img is None:
            raise FileNotFoundError(f"Nao foi possivel carregar a imagem: {image}")
        
        self.img = cv2.GaussianBlur(self.img, (5, 5), 0) 
        #adicionando filtro gaussiano para reduzir reduído e melhorar a precisão de extração de cores

        self.right_eyebrow: np.ndarray | list[object] = []
        self.left_eyebrow: np.ndarray | list[object] = []
        self.right_eye: np.ndarray | list[object] = []
        self.left_eye: np.ndarray | list[object] = []
        self.left_cheek: np.ndarray | list[object] = []
        self.right_cheek: np.ndarray | list[object] = []

        self.detect_face_part()

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

        self.right_eyebrow = self.extract_face_part(face_parts[0])
        self.left_eyebrow = self.extract_face_part(face_parts[1])
        self.right_eye = self.extract_face_part(face_parts[2])
        self.left_eye = self.extract_face_part(face_parts[3])
        self.left_cheek = self.img[shape[29][1]:shape[33][1], shape[4][0]:shape[48][0]]
        self.right_cheek = self.img[shape[29][1]:shape[33][1], shape[54][0]:shape[12][0]]

    def extract_face_part(self, face_part_points: np.ndarray) -> np.ndarray:
        x, y, w, h = cv2.boundingRect(face_part_points)
        crop = self.img[y:y + h, x:x + w]
        adj_points = np.array([np.array([p[0] - x, p[1] - y]) for p in face_part_points])
        
        mask = np.zeros((crop.shape[0], crop.shape[1]), dtype=np.uint8)
        cv2.fillConvexPoly(mask, adj_points, 1)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # fecha buracos na máscara
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)   # remove ruído nas bordas
        
        mask = mask.astype(bool)
        crop[np.logical_not(mask)] = [255, 0, 0]
        return crop
