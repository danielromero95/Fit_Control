import streamlit as st
import tempfile
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import time

# Importación directa de la función del pipeline y la configuración global
from src.pipeline import run_full_pipeline_in_memory
from src.config import settings as global_settings

# Configuración de la página
st.set_page_config(
    page_title="FitControl - Análisis de Rendimiento",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejor apariencia
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        border: 1px solid #e1e5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
    }
    .upload-section {
        border: 2px dashed #cccccc;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
    .analysis-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .progress-bar {
        height: 20px;
        background-color: #f0f0f0;
        border-radius: 10px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #4CAF50, #45a049);
        transition: width 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header principal
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0; text-align: center;">🏋️ FitControl</h1>
        <p style="color: white; margin: 0; text-align: center; opacity: 0.9;">
            Análisis Inteligente de Rendimiento Deportivo
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar con opciones
    with st.sidebar:
        st.image("assets/FitControl_logo.ico" if os.path.exists("assets/FitControl_logo.ico") else None, width=100)
        
        st.markdown("### 🎯 Modo de Análisis")
        analysis_mode = st.selectbox(
            "Selecciona el tipo de análisis:",
            ["Análisis Completo", "Contador de Repeticiones", "Análisis de Forma", "Comparación de Sesiones"]
        )
        
        st.markdown("### ⚙️ Configuración")
        
        # Configuración avanzada
        with st.expander("Configuración Avanzada"):
            sample_rate = st.slider("Tasa de muestreo", 1, 5, 1, help="Frames por segundo a procesar")
            rotation = st.selectbox("Rotación del vídeo", [0, 90, 180, 270])
            confidence_threshold = st.slider("Umbral de confianza", 0.1, 1.0, 0.5, 0.1)
            
        # Información del sistema
        with st.expander("Estado del Sistema"):
            st.success("✅ Pipeline de análisis: Activo")
            st.info("ℹ️ Modelo de pose: MediaPipe")
            st.info(f"📊 Ejercicios configurados: {len(global_settings.exercises)}")

    # Área principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Sección de carga de vídeo
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        st.markdown("### 📹 Cargar Vídeo de Entrenamiento")
        
        uploaded_video = st.file_uploader(
            "Arrastra tu vídeo aquí o haz clic para seleccionar",
            type=["mp4", "mov", "avi", "mkv"],
            help="Formatos soportados: MP4, MOV, AVI, MKV"
        )
        
        if uploaded_video is not None:
            # Guardar el vídeo subido en un fichero temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_video.name)[1]) as tfile:
                tfile.write(uploaded_video.read())
                video_path = tfile.name
            
            # Mostrar información del vídeo
            file_size = len(uploaded_video.getvalue()) / 1024 / 1024  # MB
            col_info1, col_info2, col_info3 = st.columns(3)
            
            with col_info1:
                st.metric("📁 Archivo", uploaded_video.name)
            with col_info2:
                st.metric("📊 Tamaño", f"{file_size:.1f} MB")
            with col_info3:
                st.metric("🎬 Formato", uploaded_video.type)
            
            # Previsualización del vídeo
            st.markdown("#### Previsualización")
            st.video(video_path)
            
            # Selección de ejercicio
            exercise_type = st.selectbox(
                "Tipo de ejercicio:",
                list(global_settings.exercises.keys()),
                help="Selecciona el ejercicio que se realiza en el vídeo"
            )
            
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # Panel de estadísticas rápidas
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Estadísticas Rápidas")
        
        # Métricas simuladas
        total_analyses = st.empty()
        success_rate = st.empty()
        avg_reps = st.empty()
        
        # Simulación de datos en tiempo real
        if 'stats' not in st.session_state:
            st.session_state.stats = {
                'total': 47,
                'success': 89.4,
                'avg_reps': 12.3
            }
        
        total_analyses.metric("🎯 Análisis Totales", st.session_state.stats['total'])
        success_rate.metric("✅ Tasa de Éxito", f"{st.session_state.stats['success']:.1f}%")
        avg_reps.metric("🔄 Reps Promedio", f"{st.session_state.stats['avg_reps']:.1f}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Gráfico de tendencias
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        st.markdown("### 📈 Tendencia Semanal")
        
        # Datos simulados de la semana
        days = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        reps = [15, 18, 12, 20, 16, 22, 14]
        
        fig = px.line(
            x=days, y=reps,
            title="Repeticiones por Día",
            line_shape="spline"
        )
        fig.update_layout(
            height=300,
            showlegend=False,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Botón de análisis
    if uploaded_video is not None:
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("🚀 Iniciar Análisis", type="primary", use_container_width=True):
                perform_analysis(video_path, analysis_mode, sample_rate, rotation, confidence_threshold, exercise_type)
        
        st.markdown('</div>', unsafe_allow_html=True)

def perform_analysis(video_path, analysis_mode, sample_rate, rotation, confidence_threshold, exercise_type):
    """Realiza el análisis del vídeo con feedback en tiempo real."""
    
    # Crear directorio de salida temporal
    output_dir = tempfile.mkdtemp(prefix="fitcontrol_analysis_")
    
    # Configuración del análisis
    gui_settings = {
        'output_dir': output_dir,
        'sample_rate': sample_rate,
        'rotate': rotation,
        'confidence_threshold': confidence_threshold,
        'exercise': exercise_type,
        'analysis_mode': analysis_mode,
        'generate_debug_video': True
    }
    
    # Contenedor para el progreso
    progress_container = st.container()
    
    with progress_container:
        st.markdown("### 🔄 Procesando Análisis...")
        
        # Barra de progreso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Métricas en tiempo real
        col_metric1, col_metric2, col_metric3 = st.columns(3)
        
        try:
            # Simular progreso del análisis
            phases = [
                ("Inicializando pipeline...", 10),
                ("Extrayendo frames...", 25),
                ("Detectando pose...", 50),
                ("Calculando métricas...", 75),
                ("Generando resultados...", 90),
                ("Finalizando...", 100)
            ]
            
            for phase, progress in phases:
                status_text.text(phase)
                progress_bar.progress(progress)
                time.sleep(0.5)  # Simular tiempo de procesamiento
            
            # Ejecutar análisis real
            status_text.text("Ejecutando análisis completo...")
            results = run_full_pipeline_in_memory(
                video_path=video_path,
                settings=gui_settings
            )
            
            progress_bar.progress(100)
            status_text.text("✅ Análisis completado exitosamente!")
            
            # Mostrar resultados
            display_results(results, gui_settings)
            
        except Exception as e:
            st.error(f"❌ Error durante el análisis: {str(e)}")
            st.exception(e)
        finally:
            # Limpiar archivo temporal
            if os.path.exists(video_path):
                os.unlink(video_path)

def display_results(results, settings):
    """Muestra los resultados del análisis de forma interactiva."""
    
    st.markdown("---")
    st.markdown("## 🎉 Resultados del Análisis")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🔄 Repeticiones",
            results.get('repeticiones_contadas', 'N/A'),
            delta="+2 vs anterior"
        )
    
    with col2:
        st.metric(
            "⏱️ Duración",
            f"{results.get('duracion_total', 0):.1f}s",
            delta="-5s vs anterior"
        )
    
    with col3:
        avg_speed = results.get('velocidad_promedio', 0)
        st.metric(
            "🏃 Velocidad Promedio",
            f"{avg_speed:.2f} rep/s" if avg_speed else "N/A"
        )
    
    with col4:
        quality_score = results.get('puntuacion_calidad', 0)
        st.metric(
            "⭐ Puntuación",
            f"{quality_score:.1f}/10" if quality_score else "N/A",
            delta="+0.5 vs anterior"
        )
    
    # Tabs para diferentes vistas de resultados
    tab1, tab2, tab3, tab4 = st.tabs(["📹 Vídeo Analizado", "📊 Métricas Detalladas", "📈 Gráficos", "💡 Recomendaciones"])
    
    with tab1:
        # Mostrar vídeo analizado
        debug_video = results.get("debug_video_path")
        if debug_video and os.path.exists(debug_video):
            st.markdown("### Vídeo con Análisis de Pose")
            st.video(debug_video)
        else:
            st.info("El vídeo analizado no está disponible")
    
    with tab2:
        # Mostrar métricas en DataFrame
        df_metrics = results.get("dataframe_metricas")
        if df_metrics is not None and not df_metrics.empty:
            st.markdown("### Datos por Frame")
            
            # Filtros para el DataFrame
            col_filter1, col_filter2 = st.columns(2)
            with col_filter1:
                frame_range = st.slider(
                    "Rango de frames:",
                    0, len(df_metrics)-1,
                    (0, min(100, len(df_metrics)-1))
                )
            
            with col_filter2:
                columns_to_show = st.multiselect(
                    "Columnas a mostrar:",
                    df_metrics.columns.tolist(),
                    default=df_metrics.columns.tolist()[:5]
                )
            
            # Mostrar DataFrame filtrado
            filtered_df = df_metrics.iloc[frame_range[0]:frame_range[1]][columns_to_show]
            st.dataframe(filtered_df, use_container_width=True)
            
            # Opción de descarga
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                "📥 Descargar datos CSV",
                csv,
                "analisis_metricas.csv",
                "text/csv"
            )
        else:
            st.info("No hay métricas detalladas disponibles")
    
    with tab3:
        # Gráficos interactivos
        if results.get("dataframe_metricas") is not None:
            create_interactive_charts(results["dataframe_metricas"])
        else:
            st.info("No hay datos disponibles para generar gráficos")
    
    with tab4:
        # Recomendaciones basadas en IA
        display_recommendations(results, settings)

def create_interactive_charts(df):
    """Crea gráficos interactivos con los datos del análisis."""
    
    if df.empty:
        st.warning("No hay datos para mostrar")
        return
    
    # Gráfico de velocidad a lo largo del tiempo
    if 'velocidad_angular' in df.columns:
        fig1 = px.line(
            df.reset_index(),
            x='index',
            y='velocidad_angular',
            title="Velocidad Angular a lo Largo del Tiempo",
            labels={'index': 'Frame', 'velocidad_angular': 'Velocidad (°/s)'}
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    # Gráfico de ángulos múltiples
    angle_columns = [col for col in df.columns if 'angulo' in col.lower()]
    if angle_columns:
        fig2 = go.Figure()
        for col in angle_columns[:3]:  # Mostrar máximo 3 ángulos
            fig2.add_trace(go.Scatter(
                y=df[col],
                mode='lines',
                name=col,
                line=dict(width=2)
            ))
        
        fig2.update_layout(
            title="Evolución de Ángulos Articulares",
            xaxis_title="Frame",
            yaxis_title="Ángulo (grados)",
            hovermode='x unified'
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Heatmap de correlaciones
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 1:
        correlation_matrix = df[numeric_cols].corr()
        
        fig3 = px.imshow(
            correlation_matrix,
            title="Matriz de Correlación entre Métricas",
            color_continuous_scale="RdBu_r",
            aspect="auto"
        )
        st.plotly_chart(fig3, use_container_width=True)

def display_recommendations(results, settings):
    """Muestra recomendaciones basadas en el análisis."""
    
    st.markdown("### 💡 Recomendaciones Personalizadas")
    
    reps = results.get('repeticiones_contadas', 0)
    exercise = settings.get('exercise', 'ejercicio')
    
    # Generar recomendaciones basadas en los resultados
    recommendations = []
    
    if reps > 0:
        if reps < 8:
            recommendations.append({
                "tipo": "⚡ Volumen",
                "mensaje": "Considera aumentar el número de repeticiones para mejorar la resistencia muscular.",
                "prioridad": "media"
            })
        elif reps > 15:
            recommendations.append({
                "tipo": "🎯 Intensidad",
                "mensaje": "Excelente volumen. Considera aumentar la carga para trabajar la fuerza.",
                "prioridad": "baja"
            })
    
    # Recomendaciones sobre la técnica
    quality_score = results.get('puntuacion_calidad', 0)
    if quality_score > 0:
        if quality_score < 7:
            recommendations.append({
                "tipo": "🔧 Técnica",
                "mensaje": "Enfócate en mejorar la forma del ejercicio antes de aumentar la carga.",
                "prioridad": "alta"
            })
        elif quality_score > 8.5:
            recommendations.append({
                "tipo": "🏆 Excelencia",
                "mensaje": "¡Técnica excelente! Mantén esta consistencia en tus entrenamientos.",
                "prioridad": "baja"
            })
    
    # Recomendaciones generales
    recommendations.extend([
        {
            "tipo": "📅 Planificación",
            "mensaje": f"Registra este entrenamiento de {exercise} en tu plan semanal.",
            "prioridad": "media"
        },
        {
            "tipo": "📊 Seguimiento",
            "mensaje": "Analiza videos similares semanalmente para monitorear tu progreso.",
            "prioridad": "baja"
        }
    ])
    
    # Mostrar recomendaciones por prioridad
    for priority in ["alta", "media", "baja"]:
        priority_recs = [r for r in recommendations if r["prioridad"] == priority]
        if priority_recs:
            priority_colors = {
                "alta": "🔴",
                "media": "🟡", 
                "baja": "🟢"
            }
            
            st.markdown(f"#### {priority_colors[priority]} Prioridad {priority.capitalize()}")
            
            for rec in priority_recs:
                with st.container():
                    st.markdown(f"""
                    <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #007bff;">
                        <strong>{rec['tipo']}</strong><br>
                        {rec['mensaje']}
                    </div>
                    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()