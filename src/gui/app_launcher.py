#!/usr/bin/env python3
"""
GUI Launcher para Gym Performance Analyzer
Interfaz gráfica moderna para seleccionar y ejecutar aplicaciones
"""

import sys
import os
import subprocess
import threading
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkFont
import webbrowser

class AppLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏋️ Gym Performance Analyzer - Launcher")
        self.root.geometry("800x600")
        self.root.configure(bg='#1e1e1e')
        
        # Configurar icono si existe
        try:
            icon_path = Path(__file__).parent.parent.parent / "assets" / "FitControl_logo.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass
        
        # Variables para procesos
        self.running_processes = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores oscuros
        style.configure('Title.TLabel', 
                       foreground='#ffffff', 
                       background='#1e1e1e',
                       font=('Arial', 24, 'bold'))
        
        style.configure('Subtitle.TLabel', 
                       foreground='#cccccc', 
                       background='#1e1e1e',
                       font=('Arial', 12))
        
        style.configure('Modern.TButton',
                       font=('Arial', 11, 'bold'),
                       padding=(20, 10))
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#1e1e1e')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(main_frame, 
                               text="🏋️ Gym Performance Analyzer", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, 
                                 text="Selecciona la aplicación que deseas ejecutar", 
                                 style='Subtitle.TLabel')
        subtitle_label.pack(pady=(0, 30))
        
        # Frame para botones
        buttons_frame = tk.Frame(main_frame, bg='#1e1e1e')
        buttons_frame.pack(fill='both', expand=True)
        
        # Configurar grid
        for i in range(3):
            buttons_frame.grid_columnconfigure(i, weight=1)
        for i in range(3):
            buttons_frame.grid_rowconfigure(i, weight=1)
        
        # Definir aplicaciones
        self.apps = [
            {
                'name': '🖥️ Aplicación GUI\n(PyQt)',
                'description': 'Interfaz de escritorio completa\ncon todas las funcionalidades',
                'command': './run_gui_app.sh',
                'color': '#4CAF50',
                'hover_color': '#45a049'
            },
            {
                'name': '🌐 Demo Streamlit\n(Web)',
                'description': 'Interfaz web para\nanálisis rápido',
                'command': './run_streamlit_app.sh',
                'color': '#2196F3',
                'hover_color': '#1976D2'
            },
            {
                'name': '🔧 API Django\n(Backend)',
                'description': 'Servidor API para\nentrenamientos',
                'command': './run_django_api.sh',
                'color': '#FF9800',
                'hover_color': '#F57C00'
            },
            {
                'name': '📱 App Móvil\n(React Native)',
                'description': 'Aplicación móvil\nFitControl',
                'command': './run_mobile_app.sh',
                'color': '#9C27B0',
                'hover_color': '#7B1FA2'
            },
            {
                'name': '🚀 Todas las Apps\n(Paralelo)',
                'description': 'Ejecutar múltiples\naplicaciones',
                'command': 'all',
                'color': '#F44336',
                'hover_color': '#D32F2F'
            },
            {
                'name': '🔍 Verificar Entorno\n(Check)',
                'description': 'Verificar que todo\nesté configurado',
                'command': './verificar_entorno.sh',
                'color': '#607D8B',
                'hover_color': '#455A64'
            }
        ]
        
        # Crear botones
        for i, app in enumerate(self.apps):
            row = i // 3
            col = i % 3
            
            # Frame para cada botón
            app_frame = tk.Frame(buttons_frame, bg='#1e1e1e')
            app_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            # Botón principal
            btn = tk.Button(app_frame,
                          text=app['name'],
                          bg=app['color'],
                          fg='white',
                          font=('Arial', 12, 'bold'),
                          relief='flat',
                          cursor='hand2',
                          command=lambda cmd=app['command'], name=app['name']: self.run_app(cmd, name))
            btn.pack(fill='both', expand=True, padx=5, pady=5)
            
            # Efectos hover
            btn.bind('<Enter>', lambda e, color=app['hover_color']: e.widget.configure(bg=color))
            btn.bind('<Leave>', lambda e, color=app['color']: e.widget.configure(bg=color))
            
            # Descripción
            desc_label = tk.Label(app_frame,
                                text=app['description'],
                                bg='#1e1e1e',
                                fg='#cccccc',
                                font=('Arial', 9),
                                justify='center')
            desc_label.pack(pady=(5, 0))
        
        # Frame inferior con información y botones adicionales
        bottom_frame = tk.Frame(main_frame, bg='#1e1e1e')
        bottom_frame.pack(fill='x', pady=(30, 0))
        
        # Frame para botones de acción
        action_frame = tk.Frame(bottom_frame, bg='#1e1e1e')
        action_frame.pack(side='right')
        
        # Botón para abrir documentación
        docs_btn = tk.Button(action_frame,
                           text="📚 Documentación",
                           bg='#34495e',
                           fg='white',
                           font=('Arial', 10),
                           relief='flat',
                           cursor='hand2',
                           command=self.open_docs)
        docs_btn.pack(side='left', padx=(0, 10))
        
        # Botón de salir
        exit_btn = tk.Button(action_frame,
                           text="❌ Salir",
                           bg='#e74c3c',
                           fg='white',
                           font=('Arial', 10),
                           relief='flat',
                           cursor='hand2',
                           command=self.exit_app)
        exit_btn.pack(side='left')
        
        # Estado
        self.status_label = tk.Label(bottom_frame,
                                   text="✅ Listo para ejecutar aplicaciones",
                                   bg='#1e1e1e',
                                   fg='#27ae60',
                                   font=('Arial', 10))
        self.status_label.pack(side='left')
        
    def run_app(self, command, app_name):
        """Ejecutar una aplicación"""
        def run_in_thread():
            try:
                # Cambiar al directorio raíz del proyecto
                project_root = Path(__file__).parent.parent.parent
                os.chdir(project_root)
                
                self.update_status(f"🚀 Iniciando {app_name}...", '#f39c12')
                
                if command == 'all':
                    self.run_all_apps()
                else:
                    # Hacer el script ejecutable
                    subprocess.run(['chmod', '+x', command], check=True)
                    
                    # Ejecutar el comando
                    process = subprocess.Popen(['bash', command], 
                                             stdout=subprocess.PIPE, 
                                             stderr=subprocess.PIPE)
                    
                    self.running_processes[app_name] = process
                    self.update_status(f"✅ {app_name} ejecutándose", '#27ae60')
                    
                    # Esperar a que termine
                    stdout, stderr = process.communicate()
                    
                    if process.returncode == 0:
                        self.update_status(f"✅ {app_name} completado", '#27ae60')
                    else:
                        self.update_status(f"❌ Error en {app_name}", '#e74c3c')
                        if stderr:
                            messagebox.showerror("Error", f"Error ejecutando {app_name}:\n{stderr.decode()}")
                    
                    # Limpiar del diccionario
                    if app_name in self.running_processes:
                        del self.running_processes[app_name]
                        
            except Exception as e:
                self.update_status(f"❌ Error: {str(e)}", '#e74c3c')
                messagebox.showerror("Error", f"Error ejecutando {app_name}:\n{str(e)}")
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=run_in_thread)
        thread.daemon = True
        thread.start()
    
    def run_all_apps(self):
        """Ejecutar todas las aplicaciones en paralelo"""
        apps_to_run = [
            ('./run_streamlit_app.sh', 'Streamlit'),
            ('./run_django_api.sh', 'Django API'),
            ('./run_mobile_app.sh', 'Mobile App')
        ]
        
        # Ejecutar cada app en terminal separada
        for script, name in apps_to_run:
            try:
                subprocess.run(['chmod', '+x', script], check=True)
                subprocess.Popen(['gnome-terminal', '--title', name, '--', 'bash', '-c', 
                                f'{script}; echo "Presiona Enter para cerrar..."; read'], 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                time.sleep(1)  # Pequeña pausa entre lanzamientos
            except Exception as e:
                print(f"Error launching {name}: {e}")
        
        # Ejecutar GUI app en el proceso principal
        try:
            subprocess.run(['chmod', '+x', './run_gui_app.sh'], check=True)
            subprocess.run(['bash', './run_gui_app.sh'])
        except Exception as e:
            print(f"Error launching GUI app: {e}")
    
    def update_status(self, message, color):
        """Actualizar el estado en la UI"""
        def update():
            self.status_label.configure(text=message, fg=color)
        
        self.root.after(0, update)
    
    def open_docs(self):
        """Abrir documentación"""
        docs_files = [
            "GUIA_EJECUCION.md",
            "README.md",
            "MEJORAS_IMPLEMENTADAS.md"
        ]
        
        for doc in docs_files:
            if Path(doc).exists():
                if sys.platform == 'linux':
                    subprocess.run(['xdg-open', doc])
                elif sys.platform == 'darwin':
                    subprocess.run(['open', doc])
                elif sys.platform == 'win32':
                    os.startfile(doc)
                break
    
    def exit_app(self):
        """Salir de la aplicación"""
        if self.running_processes:
            if messagebox.askyesno("Confirmar", 
                                 "Hay aplicaciones ejecutándose. ¿Quieres cerrar de todas formas?"):
                # Terminar procesos activos
                for process in self.running_processes.values():
                    try:
                        process.terminate()
                    except:
                        pass
                self.root.quit()
        else:
            self.root.quit()
    
    def run(self):
        """Ejecutar el launcher"""
        self.root.mainloop()

def main():
    """Función principal"""
    launcher = AppLauncher()
    launcher.run()

if __name__ == "__main__":
    main()