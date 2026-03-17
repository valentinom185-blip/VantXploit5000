import phonenumbers
import sys
import os
import requests
import webbrowser
from phonenumbers import geocoder, carrier, timezone
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QTextEdit, QLabel, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

class TelefonoScannerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.icon_path = os.path.join(os.path.dirname(self.script_dir), "assets") # Actualizado a 'assets'
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("VantXploit - Phone OSINT")
        self.setFixedSize(650, 620)
        
        self.setStyleSheet("""
            QWidget { background-color: #050508; color: #ffffff; font-family: 'Segoe UI', sans-serif; }
            #input_frame { background-color: #0d0d12; border: 1px solid #2a1b3d; border-radius: 8px; min-height: 45px; }
            #input_frame:focus-within { border: 1px solid #A020F0; }
            QLineEdit { background-color: transparent; border: none; color: #ffffff; font-size: 14px; padding: 5px; }
            QTextEdit { background-color: #08080a; border: 1px solid #1c1c24; border-radius: 8px; color: #e0e0e0; font-family: 'Consolas', monospace; padding: 15px; }
            QLabel#header { font-size: 24px; font-weight: 900; color: #ffffff; }
            QLabel#accent { color: #A020F0; font-weight: bold; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 20)
        layout.setSpacing(15)

        header_layout = QHBoxLayout()
        header = QLabel("PHONE LOOKUP")
        header.setObjectName("header")
        header_layout.addWidget(header)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        self.input_frame = QFrame()
        self.input_frame.setObjectName("input_frame")
        input_layout = QHBoxLayout(self.input_frame)
        input_layout.setContentsMargins(15, 0, 15, 0)
        
        self.input_phone = QLineEdit()
        self.input_phone.setPlaceholderText("Ej: +34 911 333 333 ... [Press Enter]")
        self.input_phone.returnPressed.connect(self.process_number)
        input_layout.addWidget(self.input_phone)
        layout.addWidget(self.input_frame)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.mousePressEvent = self.handle_links 
        layout.addWidget(self.console)

        footer = QLabel("VantXploit Core Module")
        footer.setStyleSheet("color: #444; font-size: 11px; font-weight: bold;")
        layout.addWidget(footer, alignment=Qt.AlignmentFlag.AlignRight)

    def handle_links(self, event):
        anchor = self.console.anchorAt(event.pos())
        if anchor: webbrowser.open(anchor)
        else: super(QTextEdit, self.console).mousePressEvent(event)

    def process_number(self):
        raw_input = self.input_phone.text().strip()
        cleaned = "".join(filter(lambda x: x.isdigit() or x == '+', raw_input))
        if cleaned and not cleaned.startswith('+'): cleaned = '+' + cleaned
        if not cleaned or len(cleaned) < 3: return

        self.console.clear()
        self.console.append(f"<span style='color:#A020F0;'>[~] Initializing scan for {cleaned}...</span><br>")
        QApplication.processEvents()

        try:
            parsed = phonenumbers.parse(cleaned, None)
            es_valido = phonenumbers.is_valid_number(parsed)
            op = carrier.name_for_number(parsed, "es") or "Unknown"
            reg = geocoder.description_for_number(parsed, "es") or "Unknown"
            pais_nom = geocoder.country_name_for_number(parsed, "es")
            
            tipos = {0: "Fijo", 1: "Móvil", 2: "Fijo/Móvil", 3: "Gratuito", 4: "Premium", 6: "VoIP"}
            tipo = tipos.get(phonenumbers.number_type(parsed), "Especial")
            
            zonas = timezone.time_zones_for_number(parsed)
            iso = phonenumbers.region_code_for_number(parsed)
            
            f_int = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            
            res = f"""
            <div style='line-height: 1.6;'>
            <b style='color:#ffffff; background-color:#1a0b2e; padding:2px 5px;'>[ TARGET ANALYSIS ]</b><br><br>
            <b style='color:#A020F0;'>[+] Status:</b> <span style='color:{'#00ff00' if es_valido else '#ffaa00'};'>{'Valid / Active' if es_valido else 'Unknown / Local'}</span><br>
            <b style='color:#A020F0;'>[+] Int. Format:</b> <span style='color:white;'>{f_int}</span><br><br>

            <b style='color:#ffffff; background-color:#1a0b2e; padding:2px 5px;'>[ GEOLOCATION ]</b><br><br>
            <b style='color:#A020F0;'>[+] Country:</b> <span style='color:white;'>{pais_nom} ({iso})</span><br>
            <b style='color:#A020F0;'>[+] Region:</b> <span style='color:white;'>{reg}</span><br>
            <b style='color:#A020F0;'>[+] Timezone:</b> <span style='color:white;'>{', '.join(zonas)}</span><br><br>

            <b style='color:#ffffff; background-color:#1a0b2e; padding:2px 5px;'>[ NETWORK INFO ]</b><br><br>
            <b style='color:#A020F0;'>[+] Carrier:</b> <span style='color:white;'>{op}</span><br>
            <b style='color:#A020F0;'>[+] Line Type:</b> <span style='color:white;'>{tipo}</span><br>
            </div>
            """
            self.console.setHtml(res)
        except Exception as e:
            self.console.setHtml(f"<b style='color:#ff4444;'>[!] Error:</b> {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TelefonoScannerUI()
    window.show()
    sys.exit(app.exec())
