import sqlite3
import logging
from typing import Dict, Any, List
from datetime import datetime

# Configuración de logging
logger = logging.getLogger(__name__)

# --- Conexión a la Base de Datos (CORREGIDA) ---
def get_db_connection() -> sqlite3.Connection:
    """Devuelve una conexión a la base de datos local 'database.db'."""
    conn = sqlite3.connect("database.db") # Usamos la ruta local para asegurar consistencia.
    conn.row_factory = sqlite3.Row
    return conn

# --- Inicialización y Creación de Tablas ---
def init_db() -> None:
    """Inicializa la base de datos y crea todas las tablas si no existen."""
    conn = get_db_connection()
    with conn:
        # Aquí van todas las sentencias CREATE TABLE...
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

# --- Población de Datos Iniciales (COMPLETA) ---
def populate_initial_exercises() -> None:
    """Inserta una lista completa de ejercicios si la tabla está vacía."""
    conn = get_db_connection()
    if conn.execute("SELECT COUNT(id) FROM exercises").fetchone()[0] > 0:
        conn.close()
        return

    logger.info("Base de datos de ejercicios vacía. Poblando con datos iniciales...")
    
    exercises = [
        {"name": "Bench Press", "muscle_group": "Pecho", "equipment": "Barra", "icon_path": "assets/exercises/chest/bench_press_icon.png", "image_full_path": "assets/exercises/chest/bench_press_full.png"},
        {"name": "Neutral Grip Pull-up", "muscle_group": "Espalda", "equipment": "Peso Corporal", "icon_path": "assets/exercises/back/neutral_grip_pull_up_icon.png", "image_full_path": "assets/exercises/back/neutral_grip_pull_up_full.png"},
        {"name": "Machine Seated Row", "muscle_group": "Espalda", "equipment": "Máquina", "icon_path": "assets/exercises/back/machine_seated_row_icon.png", "image_full_path": "assets/exercises/back/machine_seated_row_full.png"},
        {"name": "Close-Grip Cable Row", "muscle_group": "Espalda", "equipment": "Poleas", "icon_path": "assets/exercises/back/close_grip_cable_row_icon.png", "image_full_path": "assets/exercises/back/close_grip_cable_row_full.png"},
        {"name": "Close-Grip Lat Pulldown", "muscle_group": "Espalda", "equipment": "Poleas", "icon_path": "assets/exercises/back/close_grip_lat_pulldown_icon.png", "image_full_path": "assets/exercises/back/close_grip_lat_pulldown_full.png"},
        {"name": "Behind The Neck Lat Pulldown", "muscle_group": "Espalda", "equipment": "Poleas", "icon_path": "assets/exercises/back/behind_the_neck_lat_pulldown_icon.png", "image_full_path": "assets/exercises/back/behind_the_neck_lat_pulldown_full.png"},
        {"name": "Wide Grip Overhand Lat Pulldown", "muscle_group": "Espalda", "equipment": "Poleas", "icon_path": "assets/exercises/back/wide_grip_overhand_lat_pulldown_icon.png", "image_full_path": "assets/exercises/back/wide_grip_overhand_lat_pulldown_full.png"},
        {"name": "Standing Barbell Curl", "muscle_group": "Bíceps", "equipment": "Barra", "icon_path": "assets/exercises/biceps/standing_barbell_curl_icon.png", "image_full_path": "assets/exercises/biceps/standing_barbell_curl_full.png"},
        {"name": "Machine Preacher Curl", "muscle_group": "Bíceps", "equipment": "Máquina", "icon_path": "assets/exercises/biceps/machine_preacher_curl_icon.png", "image_full_path": "assets/exercises/biceps/machine_preacher_curl_full.png"},
        {"name": "Incline Dumbbell Curl", "muscle_group": "Bíceps", "equipment": "Mancuernas", "icon_path": "assets/exercises/biceps/incline_dumbbell_curl_icon.png", "image_full_path": "assets/exercises/biceps/incline_dumbbell_curl_full.png"},
        {"name": "Dumbbell Scott Curl", "muscle_group": "Bíceps", "equipment": "Mancuernas", "icon_path": "assets/exercises/biceps/dumbbell_scott_curl_icon.png", "image_full_path": "assets/exercises/biceps/dumbbell_scott_curl_full.png"},
        {"name": "Overhead Cable Curl", "muscle_group": "Bíceps", "equipment": "Poleas", "icon_path": "assets/exercises/biceps/overhead_cable_curl_icon.png", "image_full_path": "assets/exercises/biceps/overhead_cable_curl_full.png"},
        {"name": "Standing Dumbbell Curl", "muscle_group": "Bíceps", "equipment": "Mancuernas", "icon_path": "assets/exercises/biceps/standing_dumbbell_curl_icon.png", "image_full_path": "assets/exercises/biceps/standing_dumbbell_curl_full.png"},
        {"name": "Concentration Curl", "muscle_group": "Bíceps", "equipment": "Mancuernas", "icon_path": "assets/exercises/biceps/concentration_curl_icon.png", "image_full_path": "assets/exercises/biceps/concentration_curl_full.png"},
        {"name": "Dumbbell Hammer Curl", "muscle_group": "Bíceps", "equipment": "Mancuernas", "icon_path": "assets/exercises/biceps/dumbbell_hammer_curl_icon.png", "image_full_path": "assets/exercises/biceps/dumbbell_hammer_curl_full.png"},
        {"name": "Incline Barbell Curl", "muscle_group": "Bíceps", "equipment": "Barra", "icon_path": "assets/exercises/biceps/incline_barbell_curl_icon.png", "image_full_path": "assets/exercises/biceps/incline_barbell_curl_full.png"},
        {"name": "Tricep Extensions", "muscle_group": "Tríceps", "equipment": "Poleas", "icon_path": "assets/exercises/triceps/tricep_extensions_icon.png", "image_full_path": "assets/exercises/triceps/tricep_extensions_full.png"},
        {"name": "Underhand Kickbacks", "muscle_group": "Tríceps", "equipment": "Mancuernas", "icon_path": "assets/exercises/triceps/underhand_kickbacks_icon.png", "image_full_path": "assets/exercises/triceps/underhand_kickbacks_full.png"},
        {"name": "Standing Dumbbell Fly", "muscle_group": "Hombros", "equipment": "Mancuernas", "icon_path": "assets/exercises/shoulders/standing_dumbbell_fly_icon.png", "image_full_path": "assets/exercises/shoulders/standing_dumbbell_fly_full.png"},
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

def save_training_plan(title: str, plan_content_md: str) -> int:
    """Guarda un nuevo plan de entrenamiento y devuelve su ID."""
    conn = get_db_connection()
    with conn:
        cur = conn.execute(
            "INSERT INTO training_plans(title, timestamp, plan_content_md) VALUES (?, ?, ?)",
            (title, datetime.utcnow().isoformat(), plan_content_md),
        )
        plan_id = cur.lastrowid
    conn.close()
    return int(plan_id)

def get_plan_by_id(plan_id: int) -> Dict[str, Any] | None:
    """Obtiene un plan de entrenamiento por su ID."""
    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM training_plans WHERE id = ?",
        (plan_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None
    
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
