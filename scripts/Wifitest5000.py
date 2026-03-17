import sys
import os
import socket
import speedtest
import subprocess
from concurrent.futures import ThreadPoolExecutor
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QProgressBar, QFrame, QTextEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap

os.environ["QT_LOGGING_RULES"] = "*=false"

class TurboScanner(QThread):
    resultado_final = pyqtSignal(str)
    progreso = pyqtSignal(int)
    speed_data = pyqtSignal(float, float)
    log = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.dispositivos = []

    def check_ip(self, ip):
        param = "-n" if os.name == "nt" else "-c"
        try:
            res = subprocess.call(["ping", param, "1", "-w", "200", ip], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res == 0:
                try:
                    name = socket.gethostbyaddr(ip)[0]
                except:
                    name = "Unknown Host"
                return (ip, name)
        except: pass
        return None

    def run(self):
        try:
            self.log.emit("[*] MEASURING BANDWIDTH...")
            st = speedtest.Speedtest()
            st.get_best_server()
            down = st.download() / 1_000_000
            up = st.upload() / 1_000_000
            self.speed_data.emit(up, down)
            self.progreso.emit(10)

            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            base_ip = ".".join(local_ip.split(".")[:-1])

            self.log.emit(f"[*] LAUNCHING PARALLEL SWEEP ON {base_ip}.0/24...")
            ips_a_escanear = [f"{base_ip}.{i}" for i in range(1, 255)]
            
            with ThreadPoolExecutor(max_workers=50) as executor:
                resultados = list(executor.map(self.check_ip, ips_a_escanear))
            
            self.dispositivos = [r for r in resultados if r is not None]
            self.progreso.emit(90)

            res = "<pre style='font-family: Consolas, monospace; font-size: 13px; color: #e0e0e0;'>"
            res += f"<span style='color:#A020F0; font-weight:bold;'>GATEWAY  </span> ➔ {base_ip}.1\n"
            res += f"<span style='color:#A020F0; font-weight:bold;'>LOCAL IP </span> ➔ {local_ip}\n\n"
            res += "<span style='color:#ffffff; background:#1a0b2e; padding:2px;'>[ DETECTED DEVICES ON NETWORK ]</span>\n\n"
            for ip, name in self.dispositivos:
                tipo = "MODEM/GW" if ip.endswith(".1") else "HOST"
                res += f"<span style='color:#00ff00;'>+</span> {tipo.ljust(10)} ➔ <b style='color:white;'>{ip.ljust(15)}</b> | {name}\n"
            res += "</pre>"
            
            self.progreso.emit(100)
            self.resultado_final.emit(res)
        except Exception as e:
            self.resultado_final.emit(f"<span style='color:red;'>CRITICAL ERROR: {str(e)}</span>")

class ZenInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(750, 850)
        self.setWindowTitle("VantXploit - Network Recon")
        self.setStyleSheet("background-color: #050508; color: #ffffff; font-family: 'Segoe UI', sans-serif;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # --- BANNER ---
        self.banner = QLabel()
        ruta_banner = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "banner.jpg")
        if os.path.exists(ruta_banner):
            pix = QPixmap(ruta_banner)
            self.banner.setPixmap(pix.scaled(710, 130, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.banner.setText("[ ASSETS/BANNER.JPG NOT FOUND ]")
            self.banner.setStyleSheet("background: #111; color: #555; font-weight: bold;")
            self.banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.banner.setFixedHeight(130)
        layout.addWidget(self.banner)

        # --- TITULO ---
        title = QLabel("NETWORK RECONNAISSANCE & SPEED TEST")
        title.setStyleSheet("font-size: 18px; font-weight: 900; color: #ffffff; letter-spacing: 2px; padding-top: 10px;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- DASHBOARD SPEEDTEST ---
        speed_h = QHBoxLayout()
        
        self.box_down = QFrame()
        self.box_down.setStyleSheet("background: #0d0d12; border: 1px solid #1c1c24; border-radius: 8px; border-top: 3px solid #00ffff;")
        v_down = QVBoxLayout(self.box_down)
        v_down.addWidget(QLabel("DOWNLOAD SPEED", styleSheet="color:#888; font-size:11px; font-weight:bold; border:none;"), alignment=Qt.AlignmentFlag.AlignCenter)
        self.val_down = QLabel("0.0 Mbps")
        self.val_down.setStyleSheet("font-size: 32px; font-weight: bold; border:none; color: #00ffff;")
        v_down.addWidget(self.val_down, alignment=Qt.AlignmentFlag.AlignCenter)

        self.box_up = QFrame()
        self.box_up.setStyleSheet("background: #0d0d12; border: 1px solid #1c1c24; border-radius: 8px; border-top: 3px solid #A020F0;")
        v_up = QVBoxLayout(self.box_up)
        v_up.addWidget(QLabel("UPLOAD SPEED", styleSheet="color:#888; font-size:11px; font-weight:bold; border:none;"), alignment=Qt.AlignmentFlag.AlignCenter)
        self.val_up = QLabel("0.0 Mbps")
        self.val_up.setStyleSheet("font-size: 32px; font-weight: bold; border:none; color: #A020F0;")
        v_up.addWidget(self.val_up, alignment=Qt.AlignmentFlag.AlignCenter)

        speed_h.addWidget(self.box_down)
        speed_h.addWidget(self.box_up)
        layout.addLayout(speed_h)

        # --- CONTROLES ---
        self.btn = QPushButton("INITIATE FULL NETWORK SCAN (254 HOSTS)")
        self.btn.setStyleSheet("""
            QPushButton { background:#1a0b2e; color:white; font-weight:900; font-size: 14px; padding:18px; border: 1px solid #A020F0; border-radius:6px; letter-spacing: 1px;}
            QPushButton:hover { background:#A020F0; }
            QPushButton:disabled { background:#111; border: 1px solid #333; color: #555;}
        """)
        self.btn.clicked.connect(self.start)
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.btn)

        self.pbar = QProgressBar()
        self.pbar.setTextVisible(False)
        self.pbar.setStyleSheet("QProgressBar { border: none; background: #0d0d12; height: 6px; border-radius: 3px; } QProgressBar::chunk { background: #A020F0; border-radius: 3px; }")
        layout.addWidget(self.pbar)

        self.status = QLabel("SYSTEM IDLE - WAITING FOR COMMAND")
        self.status.setStyleSheet("color: #888; font-family: Consolas, monospace; font-size: 11px;")
        layout.addWidget(self.status, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- TERMINAL ---
        self.console = QTextEdit(readOnly=True)
        self.console.setStyleSheet("background:#08080a; border:1px solid #1c1c24; border-radius: 8px; padding:15px; color: #00ff00;")
        layout.addWidget(self.console)

    def start(self):
        self.btn.setEnabled(False)
        self.pbar.setValue(0)
        self.console.clear()
        self.worker = TurboScanner()
        self.worker.speed_data.connect(lambda u, d: [self.val_up.setText(f"{round(u,1)} Mbps"), self.val_down.setText(f"{round(d,1)} Mbps")])
        self.worker.progreso.connect(self.pbar.setValue)
        self.worker.log.connect(self.status.setText)
        self.worker.resultado_final.connect(lambda r: [self.console.setHtml(r), self.btn.setEnabled(True), self.status.setText("SCAN COMPLETE")])
        self.worker.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ZenInterface()
    win.show()
    sys.exit(app.exec())
