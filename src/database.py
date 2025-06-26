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
                key_metric_avg REAL,
                video_path TEXT,
                metrics_df_json TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS training_plans(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                timestamp TEXT,
                plan_content_md TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS app_state(
                key TEXT PRIMARY KEY,
                value TEXT
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

def save_training_plan(title: str, content: str) -> int:
    """Guarda un plan de entrenamiento y devuelve su ID."""
    conn = get_db_connection()
    timestamp = datetime.utcnow().isoformat()
    with conn:
        cursor = conn.execute(
            """
            INSERT INTO training_plans(title, timestamp, plan_content_md)
            VALUES (?, ?, ?)
            """,
            (title, timestamp, content),
        )
        new_id = cursor.lastrowid
    conn.close()
    return new_id

def get_all_training_plans() -> list:
    """Devuelve todos los planes guardados ordenados por fecha descendente."""
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT * FROM training_plans ORDER BY timestamp DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_plan_by_id(plan_id: int) -> Dict[str, Any] | None:
    """Obtiene un plan de entrenamiento por su ID."""
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT * FROM training_plans WHERE id = ?",
        (plan_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def set_app_state(key: str, value: str) -> None:
    """Inserta o actualiza un par clave-valor en la tabla app_state."""
    conn = get_db_connection()
    with conn:
        conn.execute(
            "INSERT OR REPLACE INTO app_state(key, value) VALUES (?, ?)",
            (key, value),
        )
    conn.close()

def get_app_state(key: str) -> str | None:
    """Recupera el valor asociado a una clave de la tabla app_state."""
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT value FROM app_state WHERE key = ?",
        (key,),
    )
    row = cursor.fetchone()
    conn.close()
    return row["value"] if row else None

def get_active_plan_id() -> int | None:
    """Devuelve el ID del plan activo almacenado en app_state."""
    val = get_app_state("active_plan_id")
    try:
        return int(val) if val is not None else None
    except (TypeError, ValueError):
        return None

def get_analysis_results_by_exercise(exercise_name: str) -> list:
    """Devuelve los análisis de un ejercicio ordenados por fecha ascendente."""
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT * FROM analysis_results WHERE exercise_name = ? ORDER BY timestamp ASC",
        (exercise_name,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_analysis_by_id(analysis_id: int) -> Dict[str, Any] | None:
    """Obtiene un único análisis por su ID."""
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT * FROM analysis_results WHERE id = ?",
        (analysis_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_analysis_by_id(analysis_id: int) -> None:
    """Elimina un análisis de la base de datos por su ID."""
    conn = get_db_connection()
    with conn:
        conn.execute(
            "DELETE FROM analysis_results WHERE id = ?",
            (analysis_id,),
        )
    conn.close()

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
        key_metric_avg = results.get("key_metric_avg")
        exercise_name = results.get("exercise") or gui_settings.get("exercise")
        video_path = results.get("debug_video_path")
        df = results.get("dataframe_metricas")
        df_json = df.to_json(orient="split") if hasattr(df, "to_json") else None
        timestamp = datetime.utcnow().isoformat()

        with conn:
            cursor = conn.execute(
                """
                INSERT INTO analysis_results(timestamp, exercise_name, rep_count, key_metric_avg, video_path, metrics_df_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (timestamp, exercise_name, rep_count, key_metric_avg, video_path, df_json),
            )
            new_id = cursor.lastrowid
        logging.info(f"Resultados guardados en la base de datos con el ID: {new_id}")
        conn.close()
        return new_id
    except Exception as e:  # pragma: no cover - tolerancia a fallos
        logging.error(f"Error al guardar en la base de datos: {e}")
        return None

def get_latest_analysis() -> Dict[str, Any] | None:
    """Devuelve el último análisis realizado."""
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT * FROM analysis_results ORDER BY timestamp DESC LIMIT 1"
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_total_analysis_count() -> int:
    """Devuelve el número total de análisis almacenados."""
    conn = get_db_connection()
    cursor = conn.execute("SELECT COUNT(id) FROM analysis_results")
    count = cursor.fetchone()[0]
    conn.close()
    try:
        return int(count)
    except (TypeError, ValueError):  # pragma: no cover - fallback
        return 0


def get_recent_reps_by_exercise(exercise_name: str, limit: int = 10) -> list:
    """Obtiene los últimos registros de un ejercicio para el gráfico principal."""
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT timestamp, rep_count FROM analysis_results WHERE exercise_name = ? ORDER BY timestamp DESC LIMIT ?",
        (exercise_name, limit),
    )
    rows = cursor.fetchall()
    conn.close()
    dict_rows = [dict(row) for row in rows]
    return list(reversed(dict_rows))
