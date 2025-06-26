import os
import sqlite3
from typing import Dict, Any, List
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
            CREATE TABLE IF NOT EXISTS exercises(
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                muscle_group TEXT,
                description_md TEXT,
                icon_path TEXT,
                image_full_path TEXT,
                equipment TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS manual_logs(
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                exercise_id INTEGER,
                reps INTEGER,
                weight REAL,
                notes TEXT,
                FOREIGN KEY(exercise_id) REFERENCES exercises(id)
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
    populate_initial_exercises()

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




def populate_initial_exercises() -> None:
    """Inserta ejercicios de ejemplo si la tabla está vacía."""
    conn = get_db_connection()
    cursor = conn.execute("SELECT COUNT(id) FROM exercises")
    count = cursor.fetchone()[0]
    if int(count) > 0:
        conn.close()
        return

    sample_exercises = [
        {
            "name": "Lat Pulldown",
            "muscle_group": "Espalda",
            "description_md": "Ejercicio para dorsales con agarre en polea.",
            "icon_path": "assets/exercises/back/lat_pulldown_icon.png",
            "image_full_path": "assets/exercises/back/lat_pulldown_full.png",
            "equipment": "Máquina",
        },
        {
            "name": "Bench Press",
            "muscle_group": "Pecho",
            "description_md": "Press de banca convencional.",
            "icon_path": "assets/exercises/chest/bench_press_icon.png",
            "image_full_path": "assets/exercises/chest/bench_press_full.png",
            "equipment": "Barra",
        },
        {
            "name": "Squat",
            "muscle_group": "Pierna",
            "description_md": "Sentadilla completa con barra.",
            "icon_path": "assets/exercises/legs/squat_icon.png",
            "image_full_path": "assets/exercises/legs/squat_full.png",
            "equipment": "Barra",
        },
    ]

    with conn:
        for ex in sample_exercises:
            conn.execute(
                """
                INSERT OR IGNORE INTO exercises(name, muscle_group, description_md, icon_path, image_full_path, equipment)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    ex["name"],
                    ex["muscle_group"],
                    ex["description_md"],
                    ex["icon_path"],
                    ex["image_full_path"],
                    ex["equipment"],
                ),
            )
    conn.close()


def get_exercises_by_group(muscle_group: str) -> List[Dict[str, Any]]:
    """Devuelve ejercicios filtrados por grupo muscular."""
    conn = get_db_connection()
    if muscle_group == "Todos":
        cursor = conn.execute("SELECT * FROM exercises ORDER BY name")
    else:
        cursor = conn.execute(
            "SELECT * FROM exercises WHERE muscle_group = ? ORDER BY name",
            (muscle_group,),
        )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_exercise_by_id(exercise_id: int) -> Dict[str, Any] | None:
    """Obtiene un ejercicio por su ID."""
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM exercises WHERE id = ?", (exercise_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_exercise_by_name(name: str) -> Dict[str, Any] | None:
    """Obtiene un ejercicio por su nombre."""
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM exercises WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_muscle_groups() -> List[str]:
    """Devuelve la lista de grupos musculares disponibles."""
    conn = get_db_connection()
    cursor = conn.execute("SELECT DISTINCT muscle_group FROM exercises ORDER BY muscle_group")
    groups = [row[0] for row in cursor.fetchall()]
    conn.close()
    return groups


def add_manual_log(
    timestamp: str,
    exercise_id: int,
    reps: int,
    weight: float,
    notes: str | None = None,
) -> int:
    """Añade un registro manual de entrenamiento."""
    conn = get_db_connection()
    with conn:
        cursor = conn.execute(
            """
            INSERT INTO manual_logs(timestamp, exercise_id, reps, weight, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (timestamp, exercise_id, reps, weight, notes),
        )
        new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_logs_for_exercise(exercise_id: int) -> List[Dict[str, Any]]:
    """Devuelve los registros manuales para un ejercicio."""
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT * FROM manual_logs WHERE exercise_id = ? ORDER BY timestamp ASC",
        (exercise_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
