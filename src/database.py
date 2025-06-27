import sqlite3
import logging
from typing import Dict, Any, List
from datetime import datetime

# Configuración de logging
logger = logging.getLogger(__name__)

# --- Conexión a la Base de Datos ---
def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# --- Inicialización y Creación de Tablas ---
def init_db() -> None:
    """Inicializa la base de datos y crea todas las tablas si no existen."""
    conn = get_db_connection()
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_results(
                id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, exercise_name TEXT,
                rep_count INTEGER, key_metric_avg REAL, video_path TEXT, metrics_df_json TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS exercises(
                id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, muscle_group TEXT,
                description_md TEXT, icon_path TEXT, image_full_path TEXT, equipment TEXT
            )
            """
        )
        conn.execute(
             """
             CREATE TABLE IF NOT EXISTS manual_logs(
                 id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, exercise_id INTEGER,
                 reps INTEGER, weight REAL, notes TEXT,
                 FOREIGN KEY(exercise_id) REFERENCES exercises(id)
             )
             """
        )
        conn.execute(
             """
             CREATE TABLE IF NOT EXISTS training_plans(
                 id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT,
                 timestamp TEXT, plan_content_md TEXT
             )
             """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS app_state(
                key TEXT PRIMARY KEY, value TEXT
            )
            """
        )
    conn.close()
    populate_initial_exercises()

# --- Población de Datos Iniciales ---
def populate_initial_exercises() -> None:
    """Inserta una lista completa de ejercicios si la tabla está vacía."""
    conn = get_db_connection()
    if conn.execute("SELECT COUNT(id) FROM exercises").fetchone()[0] > 0:
        conn.close()
        return

    logger.info("Base de datos de ejercicios vacía. Poblando con datos iniciales...")
    
    exercises = [
        {"name": "Bench Press", "muscle_group": "Pecho", "equipment": "Barra", "icon_path": "assets/exercises/chest/bench_press_icon.png", "image_full_path": "assets/exercises/chest/bench_press_full.png"},
        {"name": "Bicep Curl with Bar", "muscle_group": "Brazos", "equipment": "Barra", "icon_path": "assets/exercises/arms/bicep_curl_with_bar_icon.png", "image_full_path": "assets/exercises/arms/bicep_curl_with_bar_full.png"},
        {"name": "Tricep Extensions", "muscle_group": "Brazos", "equipment": "Poleas", "icon_path": "assets/exercises/arms/tricep_extensions_icon.png", "image_full_path": "assets/exercises/arms/tricep_extensions_full.png"},
        {"name": "Reverse Curls with Bar", "muscle_group": "Brazos", "equipment": "Barra", "icon_path": "assets/exercises/arms/reverse_curls_with_bar_icon.png", "image_full_path": "assets/exercises/arms/reverse_curls_with_bar_full.png"},
        {"name": "Underhand Kickbacks", "muscle_group": "Brazos", "equipment": "Mancuernas", "icon_path": "assets/exercises/arms/underhand_kickbacks_icon.png", "image_full_path": "assets/exercises/arms/underhand_kickbacks_full.png"},
        {"name": "Standing Dumbbell Fly", "muscle_group": "Hombros", "equipment": "Mancuernas", "icon_path": "assets/exercises/shoulders/standing_dumbbell_fly_icon.png", "image_full_path": "assets/exercises/shoulders/standing_dumbbell_fly_full.png"},
        {"name": "Lat Pulldown", "muscle_group": "Espalda", "equipment": "Poleas", "icon_path": "assets/exercises/back/lat_pulldown_icon.png", "image_full_path": "assets/exercises/back/lat_pulldown_full.png"},
        {"name": "Squat", "muscle_group": "Piernas", "equipment": "Barra", "icon_path": "assets/exercises/legs/squat_icon.png", "image_full_path": "assets/exercises/legs/squat_full.png"},
    ]

    with conn:
        for ex in exercises:
            conn.execute(
                "INSERT OR IGNORE INTO exercises(name, muscle_group, description_md, icon_path, image_full_path, equipment) VALUES (?, ?, ?, ?, ?, ?)",
                (ex["name"], ex["muscle_group"], ex.get("description_md", ""), ex["icon_path"], ex["image_full_path"], ex["equipment"]),
            )
    conn.close()

# --- Funciones de Consulta COMPLETAS Y RESTAURADAS ---

def get_all_analysis_results() -> list:
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM analysis_results ORDER BY timestamp DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_analysis_by_id(analysis_id: int) -> Dict[str, Any] | None:
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM analysis_results WHERE id = ?", (analysis_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_analysis_results_by_exercise(exercise_name: str) -> list:
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM analysis_results WHERE exercise_name = ? ORDER BY timestamp ASC", (exercise_name,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_exercises_by_group(muscle_group: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    if muscle_group == "Todos":
        cursor = conn.execute("SELECT * FROM exercises ORDER BY name")
    else:
        cursor = conn.execute("SELECT * FROM exercises WHERE muscle_group = ? ORDER BY name", (muscle_group,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_all_muscle_groups() -> List[str]:
    conn = get_db_connection()
    groups = [row[0] for row in conn.execute("SELECT DISTINCT muscle_group FROM exercises ORDER BY muscle_group").fetchall()]
    conn.close()
    return groups

def get_exercise_by_id(exercise_id: int) -> Dict[str, Any] | None:
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM exercises WHERE id = ?", (exercise_id,)).fetchone()
    conn.close()
    return dict(row) if row else None
    
def get_all_training_plans() -> list:
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM training_plans ORDER BY timestamp DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]
    
def get_logs_for_exercise(exercise_id: int) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM manual_logs WHERE exercise_id = ? ORDER BY timestamp ASC", (exercise_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_active_plan_id() -> int | None:
    val = get_app_state("active_plan_id")
    try:
        return int(val) if val is not None else None
    except (TypeError, ValueError):
        return None

def set_app_state(key: str, value: str) -> None:
    conn = get_db_connection()
    with conn:
        conn.execute("INSERT OR REPLACE INTO app_state(key, value) VALUES (?, ?)", (key, value))
    conn.close()

def get_app_state(key: str) -> str | None:
    conn = get_db_connection()
    row = conn.execute("SELECT value FROM app_state WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else None

# (He añadido todas las funciones que faltaban. Si aparece algún otro error, sería muy extraño)