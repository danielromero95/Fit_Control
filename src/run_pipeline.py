# src/run_pipeline.py

import os
import sys
import subprocess
import argparse

def check_exists_or_exit(path, mensaje):
    if not os.path.exists(path):
        print(f"[ERROR] {mensaje}: {path}")
        sys.exit(1)

def run(cmd, env=None):
    """Ejecuta un comando de shell (lista de strings). Sale si devuelve código ≠ 0."""
    print(f">>> Ejecutando: {' '.join(cmd)}")
    res = subprocess.run(cmd, env=env)
    if res.returncode != 0:
        print(f"[ERROR] El comando anterior falló con código {res.returncode}.")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline completo: extracción → preprocesado → pose → métricas → conteo")
    parser.add_argument("--video",       required=True,  help="Ruta al vídeo (ej. data/raw/1_Sq_Perfil_Parada_Sin_Camiseta.mov)")
    parser.add_argument("--fps",         type=float, required=True, help="FPS aproximado del vídeo (por ej. 28.57)")
    parser.add_argument("--sample_rate", type=int,   default=1,     help="Tomar 1 fotograma de cada N (por defecto: 1)")
    parser.add_argument("--low_thresh",  type=float, default=80.0,  help="Umbral bajo para conteo de rodilla (en grados)")
    parser.add_argument("--high_thresh", type=float, default=150.0, help="Umbral alto para conteo de rodilla (en grados)")
    parser.add_argument("--width",       type=int,   default=256,   help="Ancho de imagen final (preprocesado)")
    parser.add_argument("--height",      type=int,   default=256,   help="Alto de imagen final (preprocesado)")
    args = parser.parse_args()

    # 1) Verificar que el vídeo existe
    check_exists_or_exit(args.video, "No se encontró el vídeo de entrada")

    # 2) Definir todas las rutas de salida
    base_name       = os.path.splitext(os.path.basename(args.video))[0]
    frames_dir      = f"data/processed/frames/{base_name}"
    images_dir      = f"data/processed/images/{base_name}"
    poses_dir       = f"data/processed/poses/{base_name}"
    counts_dir      = f"data/processed/counts"
    raw_csv         = os.path.join(poses_dir, f"{base_name}_raw.csv")
    filtered_npy    = os.path.join(poses_dir, f"{base_name}_filtered.npy")
    metrics_csv     = os.path.join(poses_dir, f"{base_name}_metrics.csv")
    count_txt       = os.path.join(counts_dir, f"{base_name}_count.txt")

    # 3) Crear carpetas (si no existen)
    os.makedirs(frames_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(poses_dir, exist_ok=True)
    os.makedirs(counts_dir, exist_ok=True)

    # 4) Extracción de frames
    run([
        "python", "-m", "src.A_preprocessing.frame_extraction",
        "--input",       args.video,
        "--output",      frames_dir,
        "--sample_rate", str(args.sample_rate),
        "--rotate",      "90"  # Rotar 90 grados en sentido horario (para vídeos grabados en vertical)
    ])

    # 5) Preprocesado de imágenes (resize + normalizar)
    run([
        "python", "-m", "src.A_preprocessing.image_preprocessing",
        "--input_dir",  frames_dir,
        "--output_dir", images_dir,
        "--width",      str(args.width),
        "--height",     str(args.height),
        "--normalize"
    ])

    # 6) Detección de pose → CSV (este paso requiere mediapipe)
    #    Cambiamos temporalmente a env “gym_pose_env” para que pueda importar MediaPipe sin conflictos.
    run([
        "conda", "run", "-n", "gym_pose_env",
        "python", "-m", "src.B_pose_estimation.pose_utils",
        "to_csv",
         "--input_dir",          images_dir,
         "--output_csv",         raw_csv,
         "--visibility_threshold","0.5"
    ])

    # 7) Filtrar + interpolar → .npy (env “gym_performance_env”)
    run([
        "python", "-m", "src.B_pose_estimation.pose_utils",
        "filter_interp",
         "--input_csv",   raw_csv,
         "--output_npy",  filtered_npy,
         "--min_confidence","0.5"
    ])

    # 8) Calcular métricas → CSV
    run([
        "python", "-m", "src.B_pose_estimation.pose_utils",
        "metrics",
         "--input_npy",      filtered_npy,
         "--output_metrics", metrics_csv,
         "--fps",            str(args.fps)
    ])

    # 9) Contar repeticiones → TXT
    run([
        "python", "-m", "src.D_modeling.count_reps",
         "--input_metrics",  metrics_csv,
         "--output_count",   count_txt,
         "--knee_column",    "rodilla_izq",
         "--low_thresh",     str(args.low_thresh),
         "--high_thresh",    str(args.high_thresh)
    ])

    print("\n=== PIPELINE COMPLETADO ===")
    print(f" • Raw landmarks CSV  : {raw_csv}")
    print(f" • Secuencia .npy     : {filtered_npy}")
    print(f" • Métricas CSV       : {metrics_csv}")
    print(f" • Conteo (TXT)       : {count_txt}")
