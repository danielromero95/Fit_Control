/**
 * Tipos de datos para la API de Fit_Control
 * 
 * Interfaces que corresponden a los modelos de Django
 * y estructuras de datos de la API REST.
 */

// Tipos base de usuario y autenticación
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  date_joined: string;
  is_active: boolean;
}

export interface UserProfile {
  id: number;
  user: number;
  birth_date?: string;
  height?: number;
  weight?: number;
  fitness_level: 'beginner' | 'intermediate' | 'advanced';
  goals: string[];
  medical_conditions?: string;
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

// Tipos de ejercicios y entrenamientos
export interface Exercise {
  id: number;
  name: string;
  description: string;
  muscle_groups: string[];
  equipment_needed: string[];
  difficulty_level: 'beginner' | 'intermediate' | 'advanced';
  instructions: string[];
  tips: string[];
  image_url?: string;
  video_url?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface WorkoutPlan {
  id: number;
  name: string;
  description: string;
  difficulty_level: 'beginner' | 'intermediate' | 'advanced';
  duration_weeks: number;
  days_per_week: number;
  estimated_duration_minutes: number;
  tags: string[];
  is_public: boolean;
  created_by: number;
  created_by_name: string;
  followers_count: number;
  is_following?: boolean;
  image_url?: string;
  created_at: string;
  updated_at: string;
  workout_days: WorkoutDay[];
}

export interface WorkoutDay {
  id: number;
  plan: number;
  day_number: number;
  name: string;
  description?: string;
  exercises: WorkoutExercise[];
}

export interface WorkoutExercise {
  id: number;
  exercise: Exercise;
  sets: number;
  reps: number;
  weight?: number;
  rest_seconds: number;
  notes?: string;
  order: number;
}

// Tipos de análisis y rendimiento
export interface VideoAnalysis {
  id: number;
  user: number;
  exercise: number;
  video_file: string;
  analysis_date: string;
  repetitions_count: number;
  form_score: number;
  feedback: string;
  analysis_data: Record<string, any>;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
}

export interface UserPerformanceLog {
  id: number;
  user: number;
  exercise: number;
  workout_day?: number;
  date: string;
  sets_completed: number;
  reps_completed: number[];
  weights_used: number[];
  duration_seconds: number;
  rest_periods: number[];
  perceived_exertion: number;
  notes?: string;
  video_analysis?: VideoAnalysis;
  created_at: string;
}

export interface AnalysisMetrics {
  id: number;
  video_analysis: number;
  rep_number: number;
  joint_angles: Record<string, number>;
  movement_speed: number;
  form_deviation: number;
  timestamp: number;
}

// Tipos de estadísticas y progreso
export interface UserStats {
  workouts_this_week: number;
  workouts_this_month: number;
  current_streak: number;
  total_workouts: number;
  avg_session_duration: number;
  total_weight_lifted: number;
  favorite_exercises: Exercise[];
  progress_trends: ProgressTrend[];
}

export interface ProgressTrend {
  exercise_id: number;
  exercise_name: string;
  period: 'week' | 'month' | 'year';
  data_points: Array<{
    date: string;
    value: number;
    metric: 'weight' | 'reps' | 'duration' | 'form_score';
  }>;
}

// Tipos de respuesta de API
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: number;
}

export interface PaginatedResponse<T = any> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, any>;
}

// Tipos para filtros y búsquedas
export interface ExerciseFilters {
  muscle_groups?: string[];
  difficulty_level?: string;
  equipment_needed?: string[];
  search?: string;
}

export interface WorkoutPlanFilters {
  difficulty_level?: string;
  duration_weeks?: number;
  days_per_week?: number;
  tags?: string[];
  search?: string;
  created_by?: number;
}

// Tipos para formularios
export interface CreateWorkoutPlanData {
  name: string;
  description: string;
  difficulty_level: 'beginner' | 'intermediate' | 'advanced';
  duration_weeks: number;
  days_per_week: number;
  estimated_duration_minutes: number;
  tags: string[];
  is_public: boolean;
  workout_days: CreateWorkoutDayData[];
}

export interface CreateWorkoutDayData {
  day_number: number;
  name: string;
  description?: string;
  exercises: CreateWorkoutExerciseData[];
}

export interface CreateWorkoutExerciseData {
  exercise_id: number;
  sets: number;
  reps: number;
  weight?: number;
  rest_seconds: number;
  notes?: string;
  order: number;
}

export interface LogWorkoutData {
  exercise_id: number;
  workout_day_id?: number;
  sets_completed: number;
  reps_completed: number[];
  weights_used: number[];
  duration_seconds: number;
  rest_periods: number[];
  perceived_exertion: number;
  notes?: string;
  video_file?: File | string;
}

// Tipos específicos para pantallas
export interface TodayWorkout {
  id: number;
  plan_name: string;
  day_name: string;
  exercises: Array<{
    exercise: Exercise;
    sets: number;
    reps: number;
    rest_seconds: number;
    completed?: boolean;
  }>;
}

export interface CalendarData {
  scheduled_days: string[];
  completed_days: string[];
  streak_start?: string;
}

// Tipos para configuración de análisis
export interface ExerciseAnalysisConfig {
  id: number;
  exercise: number;
  key_points: string[];
  angle_thresholds: Record<string, { min: number; max: number }>;
  movement_patterns: Record<string, any>;
  form_criteria: Array<{
    name: string;
    weight: number;
    description: string;
  }>;
  is_active: boolean;
}

// Tipos para el análisis de video en tiempo real
export interface AnalysisResult {
  rep_count: number;
  form_score: number;
  feedback: string[];
  joint_angles: Record<string, number>;
  movement_quality: {
    speed: number;
    consistency: number;
    range_of_motion: number;
  };
  recommendations: string[];
}

export interface LiveAnalysisFrame {
  timestamp: number;
  landmarks: Array<{
    x: number;
    y: number;
    z: number;
    visibility: number;
  }>;
  angles: Record<string, number>;
  rep_phase: 'preparation' | 'concentric' | 'eccentric' | 'rest';
}

// Tipos para notificaciones y configuración
export interface UserPreferences {
  id: number;
  user: number;
  preferred_workout_time: string;
  notification_settings: {
    workout_reminders: boolean;
    progress_updates: boolean;
    new_plans: boolean;
    achievements: boolean;
  };
  privacy_settings: {
    profile_public: boolean;
    stats_public: boolean;
    workouts_public: boolean;
  };
  measurement_units: 'metric' | 'imperial';
  language: string;
  theme: 'light' | 'dark' | 'auto';
  created_at: string;
  updated_at: string;
}

export interface Achievement {
  id: number;
  name: string;
  description: string;
  icon: string;
  category: 'workout' | 'streak' | 'progress' | 'social';
  criteria: Record<string, any>;
  points: number;
  badge_color: string;
  is_earned?: boolean;
  earned_at?: string;
}

// Tipos para navegación
export interface NavigationParams {
  Today: undefined;
  Plans: undefined;
  Exercises: undefined;
  Profile: undefined;
  ExerciseDetail: { exerciseId: number };
  PlanDetail: { planId: number };
  WorkoutSession: { workoutId: number };
  VideoAnalysis: { exerciseId: number };
  Progress: undefined;
  Settings: undefined;
  Login: undefined;
  Register: undefined;
}

export default {};