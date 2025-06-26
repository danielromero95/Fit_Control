import sqlite3
import logging
from typing import Dict, Any, List

# Configuración de logging
logger = logging.getLogger(__name__)

# --- Conexión a la Base de Datos ---
def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# --- Inicialización y Creación de Tablas ---
def init_db() -> None:
    """Inicializa la base de datos y crea las tablas si no existen."""
    conn = get_db_connection()
    with conn:
        # Tabla de resultados de análisis
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
        # Tabla de ejercicios
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
    conn.close()
    # Llenamos con datos iniciales después de asegurar que las tablas existen
    populate_initial_exercises()

# --- Población de Datos Iniciales ---
def populate_initial_exercises() -> None:
    """Inserta una lista completa de ejercicios si la tabla está vacía."""
    conn = get_db_connection()
    cursor = conn.execute("SELECT COUNT(id) FROM exercises")
    count = cursor.fetchone()[0]
    if int(count) > 0:
        conn.close()
        return

    logger.info("Base de datos de ejercicios vacía. Poblando con datos iniciales...")
    
    sample_exercises = [
        # Pecho
        {"name": "Bench Press", "muscle_group": "Pecho", "equipment": "Barra", "icon_path": "assets/exercises/chest/bench_press_icon.png", "image_full_path": "assets/exercises/chest/bench_press_full.png"},
        {"name": "Incline Dumbbell Press", "muscle_group": "Pecho", "equipment": "Mancuernas", "icon_path": "assets/exercises/chest/incline_dumbbell_press_icon.png", "image_full_path": "assets/exercises/chest/incline_dumbbell_press_full.png"},
        # Espalda
        {"name": "Lat Pulldown", "muscle_group": "Espalda", "equipment": "Poleas", "icon_path": "assets/exercises/back/lat_pulldown_icon.png", "image_full_path": "assets/exercises/back/lat_pulldown_full.png"},
        # Piernas
        {"name": "Squat", "muscle_group": "Piernas", "equipment": "Barra", "icon_path": "assets/exercises/legs/squat_icon.png", "image_full_path": "assets/exercises/legs/squat_full.png"},
        # Hombros
        {"name": "Standing Dumbbell Fly", "muscle_group": "Hombros", "equipment": "Mancuernas", "icon_path": "assets/exercises/shoulders/standing_dumbbell_fly_icon.png", "image_full_path": "assets/exercises/shoulders/standing_dumbbell_fly_full.png"},
        # Brazos
        {"name": "Bicep Curl with Bar", "muscle_group": "Brazos", "equipment": "Barra", "icon_path": "assets/exercises/arms/bicep_curl_with_bar_icon.png", "image_full_path": "assets/exercises/arms/bicep_curl_with_bar_full.png"},
        {"name": "Tricep Extensions", "muscle_group": "Brazos", "equipment": "Poleas", "icon_path": "assets/exercises/arms/tricep_extensions_icon.png", "image_full_path": "assets/exercises/arms/tricep_extensions_full.png"},
        {"name": "Reverse Curls with Bar", "muscle_group": "Brazos", "equipment": "Barra", "icon_path": "assets/exercises/arms/reverse_curls_with_bar_icon.png", "image_full_path": "assets/exercises/arms/reverse_curls_with_bar_full.png"},
        {"name": "Underhand Kickbacks", "muscle_group": "Brazos", "equipment": "Mancuernas", "icon_path": "assets/exercises/arms/underhand_kickbacks_icon.png", "image_full_path": "assets/exercises/arms/underhand_kickbacks_full.png"},
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
                    ex.get("description_md", ""), # Proporcionar valor por defecto
                    ex["icon_path"],
                    ex["image_full_path"],
                    ex["equipment"],
                ),
            )
    conn.close()

# --- Funciones de Consulta ---
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

def get_all_muscle_groups() -> List[str]:
    """Devuelve la lista de grupos musculares disponibles."""
    conn = get_db_connection()
    cursor = conn.execute("SELECT DISTINCT muscle_group FROM exercises ORDER BY muscle_group")
    groups = [row[0] for row in cursor.fetchall()]
    conn.close()
    return groups

def get_exercise_by_id(exercise_id: int) -> Dict[str, Any] | None:
    """Obtiene un ejercicio por su ID."""
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM exercises WHERE id = ?", (exercise_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None
