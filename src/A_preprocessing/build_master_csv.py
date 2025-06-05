import os
import pandas as pd

def build_master_csv(public_dir, own_dir, output_csv):
    rows = []
    # Dataset público
    for root, _, files in os.walk(public_dir):
        for f in files:
            if f.endswith('.mp4'):
                ejercicio = os.path.basename(root)
                ruta = os.path.join(root, f)
                rows.append({
                    'ruta_video': ruta,
                    'ejercicio': ejercicio,
                    'voluntario_id': 'unknown',
                    'etiqueta_fallo': 'unknown',
                    'origen': 'publico'
                })
    # Dataset propio
    metadata = pd.read_csv(os.path.join(own_dir, 'metadata.csv'))
    for idx, row in metadata.iterrows():
        ruta = os.path.join(own_dir, row['ejercicio'], row['video_filename'])
        rows.append({
            'ruta_video': ruta,
            'ejercicio': row['ejercicio'],
            'voluntario_id': row['voluntario_id'],
            'etiqueta_fallo': row['etiqueta_fallo'],
            'origen': 'propio'
        })
    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)

if __name__ == '__main__':
    build_master_csv('data/raw/exercise_recognition', 'data/raw/own_videos', 'data/processed/master_dataset.csv')
