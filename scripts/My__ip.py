import sys
import requests
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt

class VisorIP(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(450, 320)
        self.setWindowTitle("VantXploit - Public IP Scanner")
        self.dibujar()

    def dibujar(self):
        self.setStyleSheet("""
            QWidget { background-color: #050508; color: #ffffff; font-family: 'Segoe UI', sans-serif; }
            #MarcoPrincipal { background-color: #0d0d12; border: 1px solid #2a1b3d; border-radius: 12px; }
            QLabel#TituloVant { font-size: 22px; font-weight: 900; color: #ffffff; }
            QLabel#SubTitulo { font-size: 12px; color: #A020F0; font-weight: bold; letter-spacing: 2px; }
            #Resultado { font-size: 28px; color: #ffffff; background: #050508; border-radius: 8px; padding: 15px; border: 1px solid #1c1c24; font-family: 'Consolas', monospace; }
            QPushButton { background: #1a0b2e; color: #ffffff; border: 1px solid #A020F0; padding: 12px; font-weight: bold; border-radius: 6px; font-size: 13px; }
            QPushButton:hover { background: #A020F0; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.marco = QFrame()
        self.marco.setObjectName("MarcoPrincipal")
        layout_marco = QVBoxLayout(self.marco)
        layout_marco.setSpacing(15)
        layout_marco.setContentsMargins(25, 25, 25, 25)

        titulo = QLabel("NETWORK IDENTITY")
        titulo.setObjectName("SubTitulo")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        titulo_main = QLabel("PUBLIC IP ADDRESS")
        titulo_main.setObjectName("TituloVant")
        titulo_main.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.etiqueta_ip = QLabel("SCANNING...")
        self.etiqueta_ip.setObjectName("Resultado")
        self.etiqueta_ip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        boton = QPushButton("REFRESH CONNECTION")
        boton.setCursor(Qt.CursorShape.PointingHandCursor)
        boton.clicked.connect(self.obtener_ip)
        
        layout_marco.addWidget(titulo)
        layout_marco.addWidget(titulo_main)
        layout_marco.addWidget(self.etiqueta_ip)
        layout_marco.addStretch()
        layout_marco.addWidget(boton)
        
        layout.addWidget(self.marco)
        self.obtener_ip()

    def obtener_ip(self):
        self.etiqueta_ip.setText("...")
        QApplication.processEvents()
        try:
            respuesta = requests.get("https://api.ipify.org?format=json", timeout=5).json()
            self.etiqueta_ip.setText(respuesta["ip"])
        except:
            self.etiqueta_ip.setText("OFFLINE")
            self.etiqueta_ip.setStyleSheet("color: #ff4444; border-color: #ff4444;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VisorIP()
    ventana.show()
    sys.exit(app.exec())