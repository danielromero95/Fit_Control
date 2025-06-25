import streamlit as st
import tempfile
import os

# Importación directa de la función del pipeline y la configuración global
from src.pipeline import run_full_pipeline_in_memory
from src.config import settings as global_settings

st.title("Gym Performance Analysis - Banco de Pruebas")

st.info("""
Esta es una interfaz de depuración rápida. Los parámetros del análisis 
(umbrales, métricas, etc.) se leen directamente de `config.yaml`.
""")

uploaded_video = st.file_uploader("Sube un vídeo para analizar", type=["mp4", "mov"])

if uploaded_video is not None:
    # Guardar el vídeo subido en un fichero temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_video.name)[1]) as tfile:
        tfile.write(uploaded_video.read())
        video_path = tfile.name
    
    st.video(video_path)

    if st.button("Empezar análisis"):
        # Creamos un directorio de salida temporal para los resultados
        output_dir = tempfile.mkdtemp(prefix="gym_streamlit_out_")
        
        # Este diccionario es para los ajustes de la GUI (como la carpeta de salida)
        # que no están en el config.yaml principal.
        gui_settings = {
            'output_dir': output_dir,
            'sample_rate': 1, # Se puede dejar fijo o añadir un control si se quiere
            'rotate': 0, # Asumimos 0 para Streamlit, se puede cambiar
            'generate_debug_video': True # Queremos ver el vídeo resultado
        }

        try:
            with st.spinner("Procesando vídeo... Esto puede tardar unos segundos."):
                # Llamada directa a la función del pipeline
                results = run_full_pipeline_in_memory(
                    video_path=video_path,
                    settings=gui_settings
                )
            
            st.success("¡Análisis completado! ✅")
            
            # Mostrar resultados clave
            st.metric(label="Repeticiones Detectadas", value=results.get('repeticiones_contadas', "N/A"))

            # Mostrar el vídeo de depuración si se generó
            debug_video = results.get("debug_video_path")
            if debug_video and os.path.exists(debug_video):
                st.markdown("### Vídeo con Análisis")
                st.video(debug_video)
            
            # Mostrar las métricas en un DataFrame interactivo
            df_metrics = results.get("dataframe_metricas")
            if df_metrics is not None and not df_metrics.empty:
                st.markdown("### Métricas por Frame")
                st.dataframe(df_metrics)
                
        except Exception as e:
            st.error("Ha ocurrido un error durante el análisis:")
            st.exception(e)
        finally:
            # Limpiar el fichero de vídeo temporal
            if os.path.exists(video_path):
                os.unlink(video_path)

