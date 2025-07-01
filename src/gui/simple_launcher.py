#!/usr/bin/env python3
"""
Simple Launcher para Gym Performance Analyzer
Versión ligera del GUI Launcher para sistemas con recursos limitados
"""

import sys
import os
import subprocess
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

class SimpleLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏋️ Gym Analyzer - Launcher")
        self.root.geometry("400x300")
        self.root.configure(bg='white')
        
        # Centrar ventana
        self.center_window()
        
        self.setup_ui()
        
    def center_window(self):
        """Centrar la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_ui(self):
        """Configurar la interfaz simple"""
        # Título
        title_label = tk.Label(self.root, 
                              text="🏋️ Gym Performance Analyzer",
                              font=('Arial', 16, 'bold'),
                              bg='white',
                              fg='#2c3e50')
        title_label.pack(pady=20)
        
        # Subtítulo
        subtitle_label = tk.Label(self.root,
                                 text="Selecciona una aplicación:",
                                 font=('Arial', 10),
                                 bg='white',
                                 fg='#7f8c8d')
        subtitle_label.pack(pady=(0, 20))
        
        # Frame para botones
        buttons_frame = tk.Frame(self.root, bg='white')
        buttons_frame.pack(expand=True, fill='both', padx=20)
        
        # Aplicaciones
        apps = [
            ("🖥️ Aplicación GUI", "./run_gui_app.sh"),
            ("🌐 Demo Web", "./run_streamlit_app.sh"),
            ("🔧 API Django", "./run_django_api.sh"),
            ("📱 App Móvil", "./run_mobile_app.sh"),
            ("🔍 Verificar Entorno", "./verificar_entorno.sh")
        ]
        
        # Crear botones
        for name, command in apps:
            btn = tk.Button(buttons_frame,
                          text=name,
                          font=('Arial', 10),
                          bg='#3498db',
                          fg='white',
                          relief='flat',
                          cursor='hand2',
                          command=lambda cmd=command, n=name: self.run_app(cmd, n))
            btn.pack(fill='x', pady=5)
            
            # Efecto hover simple
            btn.bind('<Enter>', lambda e: e.widget.configure(bg='#2980b9'))
            btn.bind('<Leave>', lambda e: e.widget.configure(bg='#3498db'))
        
        # Botón salir
        exit_btn = tk.Button(buttons_frame,
                           text="❌ Salir",
                           font=('Arial', 10),
                           bg='#e74c3c',
                           fg='white',
                           relief='flat',
                           cursor='hand2',
                           command=self.root.quit)
        exit_btn.pack(fill='x', pady=(20, 5))
        
        # Estado
        self.status_label = tk.Label(self.root,
                                   text="Listo",
                                   font=('Arial', 9),
                                   bg='white',
                                   fg='#27ae60')
        self.status_label.pack(pady=10)
        
    def run_app(self, command, app_name):
        """Ejecutar aplicación"""
        try:
            # Cambiar al directorio del proyecto
            project_root = Path(__file__).parent.parent.parent
            os.chdir(project_root)
            
            self.status_label.configure(text=f"Ejecutando {app_name}...", fg='#f39c12')
            self.root.update()
            
            # Hacer ejecutable y ejecutar
            subprocess.run(['chmod', '+x', command], check=True)
            subprocess.Popen(['bash', command])
            
            self.status_label.configure(text=f"{app_name} iniciado", fg='#27ae60')
            
        except Exception as e:
            self.status_label.configure(text="Error", fg='#e74c3c')
            messagebox.showerror("Error", f"Error ejecutando {app_name}:\n{str(e)}")
    
    def run(self):
        """Ejecutar launcher"""
        self.root.mainloop()

def main():
    """Función principal"""
    launcher = SimpleLauncher()
    launcher.run()

if __name__ == "__main__":
    main()