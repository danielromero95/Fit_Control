# src/A_preprocessing/image_preprocessing.py

import cv2
import os
import argparse
from src.A_preprocessing.file_extensions import IMAGE_EXTENSIONS  # importar extensiones de imagen

def preprocess_images(input_dir, output_dir, target_width=256, target_height=256, normalize=False):
    """
    Recorre todas las imágenes con extensiones aceptadas (definidas en IMAGE_EXTENSIONS)
    dentro de `input_dir`, las redimensiona a (target_width, target_height) y
    opcionalmente normaliza sus valores de píxel (escalar de 0–255 a 0.0–1.0). Guarda las
    imágenes resultantes en `output_dir` con el mismo nombre de archivo.

    Parámetros:
        - input_dir   : directorio donde están los fotogramas originales.
        - output_dir  : directorio donde se guardarán las imágenes procesadas.
        - target_width  : ancho al que se redimensionará cada imagen (por defecto: 256).
        - target_height : alto al que se redimensionará cada imagen (por defecto: 256).
        - normalize   : si es True, convierte el rango de píxel 0–255 a 0.0–1.0.
    Retorna:
        - total_imgs : número total de imágenes procesadas.
    """
    # Verificar que el directorio de entrada exista
    if not os.path.isdir(input_dir):
        raise NotADirectoryError(f"El directorio de entrada no existe: {input_dir}")

    # Crear directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)

    # Listar todos los archivos en el directorio de entrada que tengan una extensión válida
    all_files = sorted([
        f for f in os.listdir(input_dir)
        if os.path.splitext(f.lower())[1] in IMAGE_EXTENSIONS
    ])

    total_imgs = 0

    for filename in all_files:
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        # Leer la imagen con OpenCV (BGR)
        img = cv2.imread(input_path)
        if img is None:
            print(f"[WARNING] No se pudo leer la imagen: {input_path}")
            continue

        # Redimensionar la imagen a (target_width x target_height)
        img_resized = cv2.resize(img, (target_width, target_height), interpolation=cv2.INTER_AREA)

        # Si se pide normalizar, convertimos de 0–255 a 0.0–1.0 y luego reconvertimos a 0–255
        if normalize:
            img_resized = img_resized.astype("float32") / 255.0
            # Para guardar en JPEG volvemos a escalar a 0–255:
            img_resized = (img_resized * 255.0).astype("uint8")

        # Guardar la imagen resultado
        cv2.imwrite(output_path, img_resized)
        total_imgs += 1

    return total_imgs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Preprocesa imágenes: redimensiona y (opcionalmente) normaliza."
    )
    parser.add_argument(
        "--input_dir",
        required=True,
        help="Directorio que contiene los fotogramas extraídos (ej.: data/processed/frames/1-Squat_Own)."
    )
    parser.add_argument(
        "--output_dir",
        required=True,
        help="Directorio donde se guardarán las imágenes procesadas (ej.: data/processed/images/1-Squat_Own)."
    )
    parser.add_argument(
        "--width",
        type=int,
        default=256,
        help="Ancho al que se redimensionarán las imágenes (por defecto: 256)."
    )
    parser.add_argument(
        "--height",
        type=int,
        default=256,
        help="Alto al que se redimensionarán las imágenes (por defecto: 256)."
    )
    parser.add_argument(
        "--normalize",
        action="store_true",
        help="Si se incluye este flag, se normalizarán los valores de píxel (0–255 => 0.0–1.0)."
    )

    args = parser.parse_args()

    total = preprocess_images(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        target_width=args.width,
        target_height=args.height,
        normalize=args.normalize
    )

    print("----- Resumen de preprocesamiento -----")
    print(f"Directorio de entrada : {args.input_dir}")
    print(f"Directorio de salida  : {args.output_dir}")
    print(f"Imágenes procesadas   : {total}")
    print(f"Tamaño final (w×h)    : {args.width}×{args.height}")
    print(f"Normalize aplicado    : {args.normalize}")
    print("----- Proceso completado -----")
