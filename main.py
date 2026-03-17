import customtkinter as ctk
from PIL import Image
import os
import subprocess

# --- CONFIGURACIÓN BÁSICA ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- RENOMBRADO A VANTXPLOIT ---
        self.title("VantXploit - Advanced OSINT & Security Suite")
        self.geometry("1100x700")
        self.configure(fg_color="#050508") # Fondo oscuro profundo VantXploit

        # --- ESTRUCTURA DE LA INTERFAZ ---
        
        # 1. Barra Lateral (AHORA ES SCROLLABLE)
        self.sidebar_frame = ctk.CTkScrollableFrame(self, width=230, corner_radius=0, fg_color="#0d0d12", scrollbar_button_color="#2a1b3d", scrollbar_button_hover_color="#A020F0")
        self.sidebar_frame.pack(side="left", fill="y")

        # Título / Logo de la App en la barra (CORREGIDO weight="bold")
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text=" VantXploit", font=ctk.CTkFont(size=24, weight="bold"), text_color="#A020F0", anchor="w")
        self.logo_label.pack(padx=20, pady=(20, 20), fill="x")

        # Barra de búsqueda (Visual)
        self.search_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Search modules...", fg_color="#1c1c24", border_width=1, border_color="#2a1b3d")
        self.search_entry.pack(padx=20, pady=(0, 20), fill="x")

        # 2. Área de contenido principal (Derecha)
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#050508")
        self.main_frame.pack(side="right", fill="both", expand=True)

        # --- PANTALLA DE BIENVENIDA (Dashboard) ---
        self.setup_dashboard()

        # --- CONSTRUYENDO EL MENÚ ---
        self.construir_menu()

    def setup_dashboard(self):
        """Configura la pantalla de bienvenida con el Banner y texto en inglés"""
        
        # 1. Banner Superior
        ruta_banner = os.path.join("assets", "banner.jpg")
        self.banner_label = ctk.CTkLabel(self.main_frame, text="") # Etiqueta vacía por si no hay imagen
        
        if os.path.exists(ruta_banner):
            img_abierta = Image.open(ruta_banner)
            # Ajustar el tamaño del banner para que quede espectacular
            img_ctk = ctk.CTkImage(light_image=img_abierta, dark_image=img_abierta, size=(750, 200))
            self.banner_label.configure(image=img_ctk)
        else:
            self.banner_label.configure(text="[ BANNER IMAGE NOT FOUND IN ASSETS FOLDER ]", text_color="red")
            
        self.banner_label.pack(pady=(50, 20))

        # 2. Título de Bienvenida
        title = ctk.CTkLabel(self.main_frame, text="WELCOME TO VANTXPLOIT CORE", font=ctk.CTkFont(size=28, weight="bold"), text_color="#ffffff")
        title.pack(pady=(10, 5))

        # 3. Descripción de la herramienta en Inglés
        desc_text = (
            "Advanced Intelligence, OSINT & Network Security Suite.\n\n"
            "This framework integrates powerful reconnaissance, media extraction,\n"
            "and network analysis modules into a single centralized dashboard.\n\n"
            "Select a module from the sidebar to initialize operations.\n"
            "All tools run in isolated sub-processes to ensure core stability."
        )
        desc_label = ctk.CTkLabel(self.main_frame, text=desc_text, font=ctk.CTkFont(size=14), text_color="#888888", justify="center")
        desc_label.pack(pady=(10, 30))

        # 4. Estado del sistema (Consola pequeña abajo)
        self.status_label = ctk.CTkLabel(self.main_frame, text="[ SYSTEM IDLE - AWAITING COMMAND ]", font=ctk.CTkFont(family="Consolas", size=12), text_color="#00ff00")
        self.status_label.pack(side="bottom", pady=30)


    # --- FUNCIONES AYUDANTES PARA EL MENÚ ---
    def agregar_categoria(self, texto):
        """Añade un texto pequeño en mayúsculas para separar secciones"""
        lbl = ctk.CTkLabel(self.sidebar_frame, text=texto.upper(), text_color="#555566", font=ctk.CTkFont(size=11, weight="bold"), anchor="w")
        lbl.pack(padx=25, pady=(20, 5), fill="x")

    def agregar_boton(self, texto, nombre_imagen, nombre_script, activo=False):
        """Agrega un botón. Si tienes muchas herramientas, ahora la barra bajará sola."""
        ruta_img = os.path.join("assets", nombre_imagen)
        img_ctk = None
        if os.path.exists(ruta_img):
            img_abierta = Image.open(ruta_img)
            img_ctk = ctk.CTkImage(light_image=img_abierta, dark_image=img_abierta, size=(18, 18))

        # Colores estilo VantXploit
        color_fondo = "#1a0b2e" if activo else "transparent"
        color_hover = "#A020F0" 

        btn = ctk.CTkButton(self.sidebar_frame, 
                            text=f"  {texto}",
                            image=img_ctk,
                            anchor="w",
                            fg_color=color_fondo, 
                            hover_color=color_hover,
                            text_color="white",
                            font=ctk.CTkFont(size=13, weight="bold"),
                            height=38,
                            corner_radius=6,
                            command=lambda: self.ejecutar_script(nombre_script))
        btn.pack(padx=15, pady=3, fill="x")

    def ejecutar_script(self, nombre_script):
        """Ejecuta el archivo .py y actualiza la consola inferior"""
        ruta_script = os.path.join("scripts", nombre_script)
        
        if os.path.exists(ruta_script):
            self.status_label.configure(text=f"[ LAUNCHING MODULE: {nombre_script} ]", text_color="#A020F0")
            subprocess.Popen(["python", ruta_script])
        else:
            self.status_label.configure(text=f"[ ERROR: Module '{nombre_script}' not found in /scripts ]", text_color="#ff4444")

    # --- AQUI CONFIGURAS TU MENÚ (Puedes poner infinitas) ---
    def construir_menu(self):
        
        self.agregar_categoria("Network Intelligence")
        self.agregar_boton("Public IP Scanner", "ip.png", "My__ip.py")
        self.agregar_boton("Port Scanner", "port.png", "puertos5000.py")
        self.agregar_boton("Network Recon", "wifi.png", "Wifitest5000.py")

        self.agregar_categoria("Target OSINT")
        self.agregar_boton("Phone OSINT", "phone.png", "Telefono5000.py")
        self.agregar_boton("Email Tracker", "Email.svg", "Email_Footprint5000.py")
        self.agregar_boton("Roblox OSINT", "roblox.png", "OsintRoblox.py")

        self.agregar_categoria("Media & Utilities")
        self.agregar_boton("Media Downloader", "youtube.png", "Youtube5000.py")

        # Relleno de prueba para el scroll
        self.agregar_categoria("Coming Soon")
        for i in range(1, 10):
            self.agregar_boton(f"Locked Module 0{i}", "lock.png", "dummy.py")

if __name__ == "__main__":
    app = App()
    app.mainloop()
