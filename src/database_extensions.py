"""
Extensiones de base de datos para funcionalidades mejoradas del dashboard.
Añade nuevas consultas y funciones para métricas avanzadas y análisis.
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import json

from src.database import DATABASE_PATH

logger = logging.getLogger(__name__)


def get_total_workouts_count() -> int:
    """Obtiene el número total de entrenamientos registrados."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM analysis_results
            WHERE created_at >= datetime('now', '-30 days')
        """)
        
        result = cursor.fetchone()
        return result['total'] if result else 0
        
    except Exception as e:
        logger.error(f"Error obteniendo total de entrenamientos: {e}")
        return 0
    finally:
        if conn:
            conn.close()


def get_total_repetitions_count() -> int:
    """Obtiene el número total de repeticiones realizadas."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT SUM(CAST(json_extract(results, '$.repeticiones_contadas') AS INTEGER)) as total_reps
            FROM analysis_results
            WHERE created_at >= datetime('now', '-30 days')
            AND json_extract(results, '$.repeticiones_contadas') IS NOT NULL
        """)
        
        result = cursor.fetchone()
        return result['total_reps'] if result and result['total_reps'] else 0
        
    except Exception as e:
        logger.error(f"Error obteniendo total de repeticiones: {e}")
        return 0
    finally:
        if conn:
            conn.close()


def get_total_workout_time() -> float:
    """Obtiene el tiempo total de entrenamiento en horas."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT SUM(CAST(json_extract(results, '$.duracion_total') AS REAL)) as total_time
            FROM analysis_results
            WHERE created_at >= datetime('now', '-30 days')
            AND json_extract(results, '$.duracion_total') IS NOT NULL
        """)
        
        result = cursor.fetchone()
        total_seconds = result['total_time'] if result and result['total_time'] else 0
        return round(total_seconds / 3600, 1)  # Convertir a horas
        
    except Exception as e:
        logger.error(f"Error obteniendo tiempo total: {e}")
        return 0.0
    finally:
        if conn:
            conn.close()


def get_total_weight_lifted() -> float:
    """Estima el peso total levantado basado en ejercicios y repeticiones."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Pesos estimados por ejercicio (kg)
        exercise_weights = {
            'press_banca': 70,
            'sentadillas': 80,
            'peso_muerto': 90,
            'press_militar': 50,
            'dominadas': 75,  # peso corporal estimado
            'flexiones': 50   # porcentaje del peso corporal
        }
        
        cursor.execute("""
            SELECT 
                json_extract(gui_settings, '$.exercise') as exercise,
                SUM(CAST(json_extract(results, '$.repeticiones_contadas') AS INTEGER)) as total_reps
            FROM analysis_results
            WHERE created_at >= datetime('now', '-30 days')
            AND json_extract(results, '$.repeticiones_contadas') IS NOT NULL
            GROUP BY json_extract(gui_settings, '$.exercise')
        """)
        
        total_weight = 0
        for row in cursor.fetchall():
            exercise = row['exercise'] or 'press_banca'
            reps = row['total_reps'] or 0
            weight_per_rep = exercise_weights.get(exercise.lower(), 60)
            total_weight += reps * weight_per_rep
        
        return round(total_weight / 1000, 1)  # Convertir a toneladas
        
    except Exception as e:
        logger.error(f"Error calculando peso total: {e}")
        return 0.0
    finally:
        if conn:
            conn.close()


def get_current_week_workouts() -> int:
    """Obtiene el número de entrenamientos de la semana actual."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as weekly_count
            FROM analysis_results
            WHERE created_at >= datetime('now', 'weekday 0', '-7 days')
            AND created_at < datetime('now', 'weekday 0')
        """)
        
        result = cursor.fetchone()
        return result['weekly_count'] if result else 0
        
    except Exception as e:
        logger.error(f"Error obteniendo entrenamientos semanales: {e}")
        return 0
    finally:
        if conn:
            conn.close()


def get_weekly_progress_data() -> List[Dict[str, Any]]:
    """Obtiene datos de progreso semanal para gráficos."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                DATE(created_at) as workout_date,
                COUNT(*) as workout_count,
                SUM(CAST(json_extract(results, '$.repeticiones_contadas') AS INTEGER)) as total_reps,
                AVG(CAST(json_extract(results, '$.duracion_total') AS REAL)) as avg_duration
            FROM analysis_results
            WHERE created_at >= datetime('now', '-14 days')
            GROUP BY DATE(created_at)
            ORDER BY workout_date
        """)
        
        return [dict(row) for row in cursor.fetchall()]
        
    except Exception as e:
        logger.error(f"Error obteniendo datos de progreso: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_exercise_performance_stats() -> Dict[str, Dict[str, Any]]:
    """Obtiene estadísticas de rendimiento por ejercicio."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                json_extract(gui_settings, '$.exercise') as exercise,
                COUNT(*) as session_count,
                AVG(CAST(json_extract(results, '$.repeticiones_contadas') AS INTEGER)) as avg_reps,
                MAX(CAST(json_extract(results, '$.repeticiones_contadas') AS INTEGER)) as max_reps,
                AVG(CAST(json_extract(results, '$.duracion_total') AS REAL)) as avg_duration,
                AVG(CAST(json_extract(results, '$.puntuacion_calidad') AS REAL)) as avg_quality
            FROM analysis_results
            WHERE created_at >= datetime('now', '-30 days')
            AND json_extract(gui_settings, '$.exercise') IS NOT NULL
            GROUP BY json_extract(gui_settings, '$.exercise')
        """)
        
        stats = {}
        for row in cursor.fetchall():
            exercise = row['exercise'] or 'unknown'
            stats[exercise] = {
                'sessions': row['session_count'],
                'avg_reps': round(row['avg_reps'] or 0, 1),
                'max_reps': row['max_reps'] or 0,
                'avg_duration': round(row['avg_duration'] or 0, 1),
                'avg_quality': round(row['avg_quality'] or 0, 1)
            }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de ejercicios: {e}")
        return {}
    finally:
        if conn:
            conn.close()


def get_user_achievements() -> List[Dict[str, Any]]:
    """Obtiene logros y metas alcanzadas por el usuario."""
    try:
        achievements = []
        
        # Logro por consistencia
        week_workouts = get_current_week_workouts()
        if week_workouts >= 5:
            achievements.append({
                'type': 'consistency',
                'title': 'Guerrero Constante',
                'description': f'¡{week_workouts} entrenamientos esta semana!',
                'icon': '🔥',
                'date': datetime.now().isoformat()
            })
        
        # Logro por repeticiones
        total_reps = get_total_repetitions_count()
        if total_reps >= 1000:
            achievements.append({
                'type': 'volume',
                'title': 'Máquina de Repeticiones',
                'description': f'¡{total_reps} repeticiones completadas!',
                'icon': '💪',
                'date': datetime.now().isoformat()
            })
        
        # Logro por tiempo
        total_hours = get_total_workout_time()
        if total_hours >= 20:
            achievements.append({
                'type': 'endurance',
                'title': 'Guerrero del Tiempo',
                'description': f'¡{total_hours}h de entrenamiento!',
                'icon': '⏰',
                'date': datetime.now().isoformat()
            })
        
        return achievements
        
    except Exception as e:
        logger.error(f"Error obteniendo logros: {e}")
        return []


def get_personalized_recommendations() -> List[Dict[str, Any]]:
    """Genera recomendaciones personalizadas basadas en el historial."""
    try:
        recommendations = []
        
        # Obtener estadísticas de rendimiento
        exercise_stats = get_exercise_performance_stats()
        week_workouts = get_current_week_workouts()
        
        # Recomendación de frecuencia
        if week_workouts < 3:
            recommendations.append({
                'type': 'frequency',
                'priority': 'high',
                'title': 'Aumenta tu frecuencia',
                'message': 'Intenta entrenar al menos 3-4 veces por semana para mejores resultados.',
                'action': 'Planifica tu próximo entrenamiento'
            })
        
        # Recomendaciones por ejercicio
        for exercise, stats in exercise_stats.items():
            if stats['avg_quality'] < 7:
                recommendations.append({
                    'type': 'technique',
                    'priority': 'medium',
                    'title': f'Mejora tu técnica en {exercise}',
                    'message': f'Tu puntuación promedio es {stats["avg_quality"]:.1f}/10. Enfócate en la forma.',
                    'action': 'Ver tutoriales de técnica'
                })
        
        # Recomendación de variedad
        if len(exercise_stats) < 3:
            recommendations.append({
                'type': 'variety',
                'priority': 'low',
                'title': 'Añade variedad',
                'message': 'Incluye más ejercicios para un entrenamiento más completo.',
                'action': 'Explorar biblioteca de ejercicios'
            })
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generando recomendaciones: {e}")
        return []


def save_user_goal(goal_type: str, target_value: float, deadline: str, description: str = "") -> bool:
    """Guarda un objetivo del usuario en la base de datos."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Crear tabla de objetivos si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_type TEXT NOT NULL,
                target_value REAL NOT NULL,
                current_value REAL DEFAULT 0,
                deadline TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        
        cursor.execute("""
            INSERT INTO user_goals (goal_type, target_value, deadline, description)
            VALUES (?, ?, ?, ?)
        """, (goal_type, target_value, deadline, description))
        
        conn.commit()
        return True
        
    except Exception as e:
        logger.error(f"Error guardando objetivo: {e}")
        return False
    finally:
        if conn:
            conn.close()


def get_active_goals() -> List[Dict[str, Any]]:
    """Obtiene los objetivos activos del usuario."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM user_goals
            WHERE is_active = TRUE
            AND completed_at IS NULL
            ORDER BY created_at DESC
        """)
        
        goals = []
        for row in cursor.fetchall():
            goal = dict(row)
            
            # Calcular progreso actual basado en el tipo de objetivo
            if goal['goal_type'] == 'weekly_workouts':
                goal['current_value'] = get_current_week_workouts()
            elif goal['goal_type'] == 'monthly_reps':
                goal['current_value'] = get_total_repetitions_count()
            elif goal['goal_type'] == 'monthly_hours':
                goal['current_value'] = get_total_workout_time()
            
            # Calcular porcentaje de progreso
            if goal['target_value'] > 0:
                goal['progress_percentage'] = min(100, (goal['current_value'] / goal['target_value']) * 100)
            else:
                goal['progress_percentage'] = 0
            
            goals.append(goal)
        
        return goals
        
    except Exception as e:
        logger.error(f"Error obteniendo objetivos: {e}")
        return []
    finally:
        if conn:
            conn.close()


def update_goal_progress(goal_id: int, current_value: float) -> bool:
    """Actualiza el progreso de un objetivo específico."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Obtener el objetivo
        cursor.execute("SELECT * FROM user_goals WHERE id = ?", (goal_id,))
        goal = cursor.fetchone()
        
        if not goal:
            return False
        
        # Actualizar valor actual
        cursor.execute("""
            UPDATE user_goals 
            SET current_value = ?
            WHERE id = ?
        """, (current_value, goal_id))
        
        # Marcar como completado si se alcanzó el objetivo
        if current_value >= goal[2]:  # goal[2] es target_value
            cursor.execute("""
                UPDATE user_goals 
                SET completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (goal_id,))
        
        conn.commit()
        return True
        
    except Exception as e:
        logger.error(f"Error actualizando progreso del objetivo: {e}")
        return False
    finally:
        if conn:
            conn.close()


def get_workout_streak() -> int:
    """Calcula la racha actual de entrenamientos."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT DATE(created_at) as workout_date
            FROM analysis_results
            WHERE created_at >= datetime('now', '-30 days')
            ORDER BY workout_date DESC
        """)
        
        workout_dates = [row['workout_date'] for row in cursor.fetchall()]
        
        if not workout_dates:
            return 0
        
        # Calcular racha consecutiva
        streak = 0
        current_date = datetime.now().date()
        
        for workout_date in workout_dates:
            workout_date_obj = datetime.strptime(workout_date, '%Y-%m-%d').date()
            
            # Si el entrenamiento fue hoy o ayer, continuar la racha
            days_diff = (current_date - workout_date_obj).days
            
            if days_diff <= streak + 1:
                streak += 1
                current_date = workout_date_obj
            else:
                break
        
        return streak
        
    except Exception as e:
        logger.error(f"Error calculando racha: {e}")
        return 0
    finally:
        if conn:
            conn.close()


def export_user_data() -> Dict[str, Any]:
    """Exporta todos los datos del usuario para backup o análisis."""
    try:
        data = {
            'export_date': datetime.now().isoformat(),
            'total_workouts': get_total_workouts_count(),
            'total_repetitions': get_total_repetitions_count(),
            'total_hours': get_total_workout_time(),
            'total_weight': get_total_weight_lifted(),
            'current_streak': get_workout_streak(),
            'weekly_progress': get_weekly_progress_data(),
            'exercise_stats': get_exercise_performance_stats(),
            'achievements': get_user_achievements(),
            'active_goals': get_active_goals(),
            'recommendations': get_personalized_recommendations()
        }
        
        return data
        
    except Exception as e:
        logger.error(f"Error exportando datos: {e}")
        return {}


# Agregar estas funciones al módulo database principal
def extend_database_module():
    """Extiende el módulo database con las nuevas funciones."""
    import src.database as db
    
    # Agregar las nuevas funciones al módulo database
    db.get_total_workouts_count = get_total_workouts_count
    db.get_total_repetitions_count = get_total_repetitions_count
    db.get_total_workout_time = get_total_workout_time
    db.get_total_weight_lifted = get_total_weight_lifted
    db.get_current_week_workouts = get_current_week_workouts
    db.get_weekly_progress_data = get_weekly_progress_data
    db.get_exercise_performance_stats = get_exercise_performance_stats
    db.get_user_achievements = get_user_achievements
    db.get_personalized_recommendations = get_personalized_recommendations
    db.get_workout_streak = get_workout_streak
    db.save_user_goal = save_user_goal
    db.get_active_goals = get_active_goals
    db.update_goal_progress = update_goal_progress
    db.export_user_data = export_user_data


# Ejecutar extensión automáticamente al importar
extend_database_module()