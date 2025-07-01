# Solución de Problemas de Dependencias - Gym Performance Analyzer

## Problemas Identificados

### 1. **ModuleNotFoundError: No module named 'plotly'**
- **Causa**: La librería `plotly` no está instalada en el entorno conda
- **Solución**: Ejecutar `pip install plotly>=5.0.0`

### 2. **ModuleNotFoundError: No module named 'src'**
- **Causa**: Python no puede encontrar el módulo `src` porque no está en el `PYTHONPATH`
- **Solución**: Agregar el directorio raíz del proyecto al `PYTHONPATH`

### 3. **OSError: [Errno 2] No such file or directory**
- **Causa**: Problemas con la instalación de conda/archivos corruptos
- **Solución**: Reinstalar el entorno conda desde cero

## Soluciones Rápidas

### 🚀 Solución Inmediata (Recomendada)
Ejecuta el script de reparación rápida:
```bash
fix_dependencies.bat
```

### 🔧 Solución Completa
Si la solución rápida no funciona, reinstala todo:
```bash
setup_windows_fixed.bat
```

### 🛠️ Solución Manual
Si prefieres instalar manualmente:

1. **Activar el entorno:**
   ```bash
   conda activate gym_env
   ```

2. **Instalar dependencias faltantes:**
   ```bash
   pip install plotly>=5.0.0
   pip install requests>=2.25.0
   pip install --force-reinstall protobuf<5,>=4.25.3
   ```

3. **Ejecutar con PYTHONPATH correcto:**
   ```bash
   cd C:\Users\drmdg\Desktop\Fit_Control
   set PYTHONPATH=%CD%;%PYTHONPATH%
   python src/gui/main.py
   ```

## Scripts Actualizados

### 📁 `run_gui_app.bat` - Corregido
- Ahora incluye configuración del `PYTHONPATH`
- Verifica e instala dependencias faltantes automáticamente
- Incluye `plotly` y `requests` en las verificaciones

### 📁 `run_streamlit_app.bat` - Corregido  
- Configuración mejorada del entorno
- Verificación completa de dependencias

### 📁 `environment.yml` - Actualizado
- Agregadas dependencias faltantes: `plotly` y `requests`

## Verificación de la Instalación

Para verificar que todo funciona correctamente:

```python
# Ejecuta este código en Python para verificar
import sys
print("Python version:", sys.version)

# Verificar dependencias críticas
modules = ['PyQt5', 'cv2', 'mediapipe', 'plotly', 'requests', 'streamlit']
for module in modules:
    try:
        __import__(module)
        print(f"✓ {module} - OK")
    except ImportError as e:
        print(f"✗ {module} - FALTA: {e}")

# Verificar módulos src
try:
    from src.i18n.translator import Translator
    print("✓ src.i18n.translator - OK")
except ImportError as e:
    print(f"✗ src.i18n.translator - FALTA: {e}")
```

## Próximos Pasos

1. **Ejecuta** `fix_dependencies.bat`
2. **Verifica** que todas las dependencias están instaladas
3. **Prueba** ejecutar `run_gui_app.bat` o `run_streamlit_app.bat`
4. Si aún hay problemas, ejecuta `setup_windows_fixed.bat` para una instalación limpia

## Contacto y Soporte

Si sigues teniendo problemas:
- Revisa los logs en la carpeta `logs/`
- Ejecuta los scripts desde una terminal de Anaconda
- Asegúrate de tener permisos de administrador si es necesario