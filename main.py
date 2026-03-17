import customtkinter as ctk
from PIL import Image
import os
import subprocess

# --- CONFIGURACIÓN BÁSICA ---
ctk.set_appearance_mode("dark")  # Modo oscuro por defecto
ctk.set_default_color_theme("dark-blue")  # Tema de colores

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        self.title("Indicia Tool")
        self.geometry("1000x600")
        self.configure(fg_color="#0d0d0d") # Fondo oscuro principal

        # --- ESTRUCTURA DE LA INTERFAZ ---
        # 1. Barra Lateral (Sidebar) a la izquierda
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#141417")
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False) # Evita que se encoja

        # Título / Logo de la App
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="  Indicia", font=ctk.CTkFont(size=20, weight="bold"), anchor="w")
        self.logo_label.pack(padx=20, pady=(20, 10), fill="x")

        # Barra de búsqueda (Visual)
        self.search_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Search...", fg_color="#1c1c21", border_width=0)
        self.search_entry.pack(padx=20, pady=(0, 20), fill="x")

        # Área de contenido (Derecha) - Aquí pasará la acción de tus scripts si decides integrarlos visualmente
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        self.main_label = ctk.CTkLabel(self.main_frame, text="Bienvenido. Selecciona una herramienta.", font=ctk.CTkFont(size=24))
        self.main_label.pack(expand=True)

        # --- CONSTRUYENDO EL MENÚ ---
        # Aquí es donde configuras tus botones e imágenes
        self.construir_menu()

    # --- FUNCIONES AYUDANTES PARA EL MENÚ ---
    def agregar_categoria(self, texto):
        """Añade un texto pequeño en mayúsculas para separar secciones"""
        lbl = ctk.CTkLabel(self.sidebar_frame, text=texto.upper(), text_color="#6b6b75", font=ctk.CTkFont(size=10, weight="bold"), anchor="w")
        lbl.pack(padx=25, pady=(15, 5), fill="x")

    def agregar_boton(self, texto, nombre_imagen, nombre_script, activo=False):
        """Agrega un botón perfectamente alineado. 
        Asegúrate de que tus imágenes estén en la carpeta 'assets' y tus scripts en 'scripts'."""
        
        # Ruta de la imagen
        ruta_img = os.path.join("assets", nombre_imagen)
        
        # Cargar imagen (Si no existe, no falla brutalmente, solo no muestra nada)
        img_ctk = None
        if os.path.exists(ruta_img):
            img_abierta = Image.open(ruta_img)
            img_ctk = ctk.CTkImage(light_image=img_abierta, dark_image=img_abierta, size=(18, 18))

        # Colores dependiendo de si el botón está "activo" (como Roblox en tu foto)
        color_fondo = "#2d2d5e" if activo else "transparent"
        color_hover = "#2d2d5e" if not activo else "#3d3d7a"

        # Crear el botón
        btn = ctk.CTkButton(self.sidebar_frame, 
                            text=f"  {texto}", # Espacio para separar texto del icono
                            image=img_ctk,
                            anchor="w",       # Alineación perfecta a la izquierda
                            fg_color=color_fondo, 
                            hover_color=color_hover,
                            text_color="white",
                            font=ctk.CTkFont(size=13),
                            height=35,
                            corner_radius=6,
                            command=lambda: self.ejecutar_script(nombre_script))
        btn.pack(padx=15, pady=2, fill="x")

    def ejecutar_script(self, nombre_script):
        """Esta función ejecuta tu archivo .py externo"""
        self.main_label.configure(text=f"Ejecutando: {nombre_script}...")
        ruta_script = os.path.join("scripts", nombre_script)
        
        if os.path.exists(ruta_script):
            # Ejecuta el script de Python en un proceso separado para que no se congele el menú
            subprocess.Popen(["python", ruta_script])
        else:
            self.main_label.configure(text=f"Error: No se encontró scripts/{nombre_script}")

    # --- AQUI CONFIGURAS TU MENÚ FACILMENTE ---
    def construir_menu(self):
        # Ejemplo: Categoría 1
        self.agregar_categoria("Infrastructure")
        # Formato: self.agregar_boton("Texto", "icono.png", "archivo.py")
        self.agregar_boton("IP Info", "ip.png", "ip_info.py")
        self.agregar_boton("Port Scan", "port.png", "port_scan.py")

        # Ejemplo: Categoría 2
        self.agregar_categoria("Social")
        self.agregar_boton("Usernames", "user.png", "user_search.py")
        self.agregar_boton("Roblox", "roblox.png", "roblox_tool.py", activo=True) # Resaltado como en tu foto
        self.agregar_boton("Discord", "discord.png", "discord_tool.py")

        # Ejemplo: Categoría 3
        self.agregar_categoria("Tools")
        self.agregar_boton("Admin Panel", "admin.png", "admin.py")

if __name__ == "__main__":
    app = App()
    app.mainloop()
