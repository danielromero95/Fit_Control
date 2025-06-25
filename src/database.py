import os
import sqlite3
from typing import Dict, Any
from datetime import datetime
import logging

from src.constants import DB_PATH

def get_db_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    conn = get_db_connection()
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_results(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                exercise_name TEXT,
                rep_count INTEGER,
                video_path TEXT,
                metrics_df_json TEXT
            )
            """
        )
    conn.close()

def get_all_analysis_results() -> list:
    """Devuelve todos los análisis guardados ordenados por fecha descendente."""
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT * FROM analysis_results ORDER BY timestamp DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_analysis_results(results: Dict[str, Any], gui_settings: Dict[str, Any]) -> int | None:
    """Guarda los resultados de un análisis.

    Parameters
    ----------
    results: dict
        Diccionario retornado por el pipeline.
    gui_settings: dict
        Ajustes utilizados al lanzar el análisis.

    Returns
    -------
    int | None
        El ID de la fila insertada o ``None`` si ocurre un error.
    """

    try:
        conn = get_db_connection()
        rep_count = results.get("repeticiones_contadas")
        exercise_name = results.get("exercise") or gui_settings.get("exercise")
        video_path = results.get("debug_video_path")
        df = results.get("dataframe_metricas")
        df_json = df.to_json(orient="split") if hasattr(df, "to_json") else None
        timestamp = datetime.utcnow().isoformat()

        with conn:
            cursor = conn.execute(
                """
                INSERT INTO analysis_results(timestamp, exercise_name, rep_count, video_path, metrics_df_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (timestamp, exercise_name, rep_count, video_path, df_json),
            )
            new_id = cursor.lastrowid
        logging.info(f"Resultados guardados en la base de datos con el ID: {new_id}")
        conn.close()
        return new_id
    except Exception as e:  # pragma: no cover - tolerancia a fallos
        logging.error(f"Error al guardar en la base de datos: {e}")
        return None
