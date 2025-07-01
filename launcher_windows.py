#!/usr/bin/env python3
"""
GUI Launcher para Gym Performance Analyzer - Versión Windows
Interfaz gráfica moderna optimizada para Windows 11
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
import platform

class WindowsAppLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏋️ Gym Performance Analyzer")
        self.root.geometry("900x700")
        
        # Configurar para Windows 11
        if platform.system() == "Windows":
            try:
                # Estilo moderno de Windows 11
                self.root.configure(bg='#f3f3f3')
                # Intentar usar el tema de Windows
                self.root.tk.call('source', 'azure.tcl')
                self.root.tk.call('set_theme', 'light')
            except:
                self.root.configure(bg='#f0f0f0')
        
        # Configurar icono si existe
        try:
            icon_path = Path(__file__).parent / "assets" / "FitControl_logo.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass
        
        # Variables para procesos
        self.running_processes = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar la interfaz de usuario moderna para Windows 11"""
        # Estilo moderno
        style = ttk.Style()
        
        # Configurar tema claro moderno
        style.configure('Title.TLabel', 
                       foreground='#2d2d2d', 
                       background='#f3f3f3',
                       font=('Segoe UI', 28, 'bold'))
        
        style.configure('Subtitle.TLabel', 
                       foreground='#666666', 
                       background='#f3f3f3',
                       font=('Segoe UI', 12))
        
        style.configure('Modern.TButton',
                       font=('Segoe UI', 11, 'bold'),
                       padding=(20, 15))
        
        # Frame principal con padding moderno
        main_frame = tk.Frame(self.root, bg='#f3f3f3')
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Header con título y descripción
        header_frame = tk.Frame(main_frame, bg='#f3f3f3')
        header_frame.pack(fill='x', pady=(0, 40))
        
        title_label = ttk.Label(header_frame, 
                               text="🏋️ Gym Performance Analyzer", 
                               style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, 
                                 text="Análisis inteligente de rendimiento deportivo", 
                                 style='Subtitle.TLabel')
        subtitle_label.pack(pady=(5, 0))
        
        # Frame para las tarjetas de aplicaciones
        apps_frame = tk.Frame(main_frame, bg='#f3f3f3')
        apps_frame.pack(fill='both', expand=True)
        
        # Configurar grid responsivo
        for i in range(2):
            apps_frame.grid_columnconfigure(i, weight=1)
        for i in range(3):
            apps_frame.grid_rowconfigure(i, weight=1)
        
        # Definir aplicaciones con comandos para Windows
        self.apps = [
            {
                'name': '🖥️ Aplicación de Escritorio',
                'subtitle': 'Interfaz completa PyQt',
                'description': 'Análisis completo de movimientos\ncon interfaz de escritorio nativa',
                'command': 'run_gui_app.bat',
                'color': '#0078d4',
                'hover_color': '#106ebe',
                'icon': '🖥️'
            },
            {
                'name': '🌐 Interfaz Web',
                'subtitle': 'Demo rápido Streamlit',
                'description': 'Análisis web interactivo\npara pruebas rápidas',
                'command': 'run_streamlit_app.bat',
                'color': '#00bcf2',
                'hover_color': '#0099cc',
                'icon': '🌐'
            },
            {
                'name': '📱 Aplicación Móvil',
                'subtitle': 'React Native (Desarrollo)',
                'description': 'App móvil multiplataforma\n(requiere emulador Android)',
                'command': 'info_mobile',
                'color': '#7b68ee',
                'hover_color': '#6a5acd',
                'icon': '📱'
            },
            {
                'name': '🔧 Configuración',
                'subtitle': 'Setup automático',
                'description': 'Configurar entorno y\nverificar dependencias',
                'command': 'setup_windows.bat',
                'color': '#ff8c00',
                'hover_color': '#e67c00',
                'icon': '🔧'
            }
        ]
        
        # Crear tarjetas de aplicaciones con diseño moderno
        for i, app in enumerate(self.apps):
            row = i // 2
            col = i % 2
            
            # Card frame con sombra simulada
            card_frame = tk.Frame(apps_frame, bg='#ffffff', relief='flat', bd=0)
            card_frame.grid(row=row, column=col, padx=15, pady=15, sticky='nsew')
            
            # Añadir efecto de borde suave
            card_inner = tk.Frame(card_frame, bg='#ffffff', relief='solid', bd=1)
            card_inner.pack(fill='both', expand=True, padx=2, pady=2)
            
            # Header de la card
            card_header = tk.Frame(card_inner, bg=app['color'], height=60)
            card_header.pack(fill='x')
            card_header.pack_propagate(False)
            
            icon_label = tk.Label(card_header,
                                text=app['icon'],
                                bg=app['color'],
                                fg='white',
                                font=('Segoe UI', 24))
            icon_label.pack(side='left', padx=20, pady=15)
            
            title_frame = tk.Frame(card_header, bg=app['color'])
            title_frame.pack(side='left', fill='both', expand=True, pady=10)
            
            title_label = tk.Label(title_frame,
                                 text=app['name'],
                                 bg=app['color'],
                                 fg='white',
                                 font=('Segoe UI', 14, 'bold'),
                                 anchor='w')
            title_label.pack(fill='x')
            
            subtitle_label = tk.Label(title_frame,
                                    text=app['subtitle'],
                                    bg=app['color'],
                                    fg='#e6f3ff',
                                    font=('Segoe UI', 10),
                                    anchor='w')
            subtitle_label.pack(fill='x')
            
            # Contenido de la card
            card_content = tk.Frame(card_inner, bg='#ffffff')
            card_content.pack(fill='both', expand=True, padx=20, pady=20)
            
            desc_label = tk.Label(card_content,
                                text=app['description'],
                                bg='#ffffff',
                                fg='#666666',
                                font=('Segoe UI', 10),
                                justify='left',
                                anchor='nw')
            desc_label.pack(fill='both', expand=True)
            
            # Botón de acción
            btn = tk.Button(card_content,
                          text="Ejecutar",
                          bg=app['color'],
                          fg='white',
                          font=('Segoe UI', 11, 'bold'),
                          relief='flat',
                          cursor='hand2',
                          activebackground=app['hover_color'],
                          command=lambda cmd=app['command'], name=app['name']: self.run_app(cmd, name))
            btn.pack(fill='x', pady=(10, 0))
            
            # Efectos hover para la card completa
            def on_enter(event, frame=card_inner, color=app['hover_color']):
                frame.configure(relief='solid', bd=2)
            
            def on_leave(event, frame=card_inner):
                frame.configure(relief='solid', bd=1)
            
            card_inner.bind('<Enter>', on_enter)
            card_inner.bind('<Leave>', on_leave)
        
        # Frame inferior con información y controles
        bottom_frame = tk.Frame(main_frame, bg='#f3f3f3')
        bottom_frame.pack(fill='x', pady=(30, 0))
        
        # Estado
        self.status_label = tk.Label(bottom_frame,
                                   text="✅ Sistema listo",
                                   bg='#f3f3f3',
                                   fg='#107c10',
                                   font=('Segoe UI', 10, 'bold'))
        self.status_label.pack(side='left')
        
        # Botones de acción
        action_frame = tk.Frame(bottom_frame, bg='#f3f3f3')
        action_frame.pack(side='right')
        
        docs_btn = tk.Button(action_frame,
                           text="📚 Documentación",
                           bg='#5a5a5a',
                           fg='white',
                           font=('Segoe UI', 10),
                           relief='flat',
                           cursor='hand2',
                           command=self.open_docs)
        docs_btn.pack(side='left', padx=(0, 10))
        
        exit_btn = tk.Button(action_frame,
                           text="❌ Salir",
                           bg='#d13438',
                           fg='white',
                           font=('Segoe UI', 10),
                           relief='flat',
                           cursor='hand2',
                           command=self.exit_app)
        exit_btn.pack(side='left')
        
    def run_app(self, command, app_name):
        """Ejecutar una aplicación específica para Windows"""
        def run_in_thread():
            try:
                project_root = Path(__file__).parent
                os.chdir(project_root)
                
                self.update_status(f"🚀 Iniciando {app_name}...", '#ff8c00')
                
                if command == 'info_mobile':
                    self.show_mobile_info()
                elif command.endswith('.bat'):
                    # Ejecutar script batch de Windows
                    if not Path(command).exists():
                        self.update_status(f"❌ Archivo {command} no encontrado", '#d13438')
                        messagebox.showerror("Error", f"No se encontró el archivo {command}")
                        return
                    
                    # Ejecutar en nueva ventana de cmd
                    process = subprocess.Popen(['cmd', '/c', 'start', 'cmd', '/k', command], 
                                             shell=True)
                    
                    self.update_status(f"✅ {app_name} iniciado", '#107c10')
                else:
                    # Comando personalizado
                    process = subprocess.run(command, shell=True, check=True)
                    
            except Exception as e:
                self.update_status(f"❌ Error: {str(e)}", '#d13438')
                messagebox.showerror("Error", f"Error ejecutando {app_name}:\n{str(e)}")
        
        thread = threading.Thread(target=run_in_thread)
        thread.daemon = True
        thread.start()
    
    def show_mobile_info(self):
        """Mostrar información sobre la aplicación móvil"""
        info_text = """
📱 Aplicación Móvil FitControl (React Native)

INFORMACIÓN IMPORTANTE:

✅ QUÉ TENEMOS:
• Una aplicación móvil completa React Native
• Compatible con Android e iOS
• Interfaz nativa optimizada

⚠️ PARA EJECUTAR NECESITAS:

1. EMULADOR ANDROID:
   • Android Studio con AVD Manager
   • O dispositivo Android físico

2. DESARROLLO iOS (solo en macOS):
   • Xcode con simulador iOS
   • O dispositivo iOS físico

3. ENTORNO DE DESARROLLO:
   • Node.js (v16 o superior)
   • React Native CLI
   • Java Development Kit (JDK)

🔧 CONFIGURACIÓN AUTOMÁTICA:
Próximamente crearemos scripts automáticos para:
• Instalar Android Studio
• Configurar emuladores
• Ejecutar la app móvil

💡 RECOMENDACIÓN ACTUAL:
Usa la aplicación de escritorio (PyQt) que tiene
todas las funcionalidades y no requiere emulador.
        """
        
        mobile_window = tk.Toplevel(self.root)
        mobile_window.title("📱 Información Aplicación Móvil")
        mobile_window.geometry("500x600")
        mobile_window.configure(bg='#f3f3f3')
        
        text_widget = tk.Text(mobile_window, 
                            wrap='word', 
                            bg='#ffffff',
                            fg='#2d2d2d',
                            font=('Segoe UI', 10),
                            padx=20,
                            pady=20)
        text_widget.pack(fill='both', expand=True, padx=20, pady=20)
        text_widget.insert('1.0', info_text)
        text_widget.configure(state='disabled')
    
    def update_status(self, message, color):
        """Actualizar el estado en la UI"""
        def update():
            self.status_label.configure(text=message, fg=color)
        
        self.root.after(0, update)
    
    def open_docs(self):
        """Abrir documentación"""
        docs_files = [
            "README.md",
            "GUIA_EJECUCION.md",
            "FACILIDAD_DE_USO.md"
        ]
        
        for doc in docs_files:
            if Path(doc).exists():
                os.startfile(doc)
                break
    
    def exit_app(self):
        """Salir de la aplicación"""
        self.root.quit()
    
    def run(self):
        """Ejecutar el launcher"""
        self.root.mainloop()

def main():
    """Función principal"""
    launcher = WindowsAppLauncher()
    launcher.run()

if __name__ == "__main__":
    main()