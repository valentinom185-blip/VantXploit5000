import sys
import os
import socket
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QTextEdit, QLabel, QFrame, QPushButton)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap

os.environ["QT_LOGGING_RULES"] = "*=false"

class ScannerWorker(QThread):
    resultado = pyqtSignal(int, str)
    finalizado = pyqtSignal()

    def __init__(self, ip, start_p, end_p):
        super().__init__()
        self.ip = ip
        self.start_p = start_p
        self.end_p = end_p

    def run(self):
        for port in range(self.start_p, self.end_p + 1):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.3)
            if sock.connect_ex((self.ip, port)) == 0:
                self.resultado.emit(port, "OPEN")
            sock.close()
        self.finalizado.emit()

class PortScannerZen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("VantXploit - Advanced Port Scanner")
        self.setFixedSize(600, 750)
        
        self.setStyleSheet("""
            QWidget { background-color: #050508; color: #ffffff; font-family: 'Segoe UI', sans-serif; }
            .InputFrame { background-color: #0d0d12; border: 1px solid #1c1c24; border-radius: 8px; margin-bottom: 10px; padding: 5px; }
            .InputFrame:focus-within { border: 1px solid #A020F0; }
            QLineEdit { background: transparent; border: none; color: white; font-size: 14px; padding: 5px; }
            QPushButton#main_btn { background: #1a0b2e; border: 1px solid #A020F0; border-radius: 6px; color: white; padding: 15px; font-weight: 900; font-size: 13px; letter-spacing: 1px; }
            QPushButton#main_btn:hover { background: #A020F0; }
            QPushButton#main_btn:disabled { background: #111; border-color: #333; color: #555; }
            QPushButton#firewall_btn { background: #1a0505; color: #ff4444; border: 1px solid #ff4444; border-radius: 6px; font-weight: bold; padding: 10px; }
            QPushButton#firewall_btn:hover { background: #ff4444; color: white; }
            QTextEdit { background: #08080a; border: 1px solid #1c1c24; border-radius: 8px; color: #e0e0e0; font-family: 'Consolas', monospace; padding: 15px; }
            QLabel#label_txt { color: #888; font-size: 11px; font-weight: bold; margin-bottom: 2px; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        # --- BANNER ---
        self.banner = QLabel()
        ruta_banner = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "banner.jpg")
        if os.path.exists(ruta_banner):
            self.banner.setPixmap(QPixmap(ruta_banner).scaled(540, 100, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.banner.setText("[ ASSETS/BANNER.JPG NOT FOUND ]")
            self.banner.setStyleSheet("background: #111; color: #555; font-weight: bold;")
            self.banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.banner.setFixedHeight(100)
        layout.addWidget(self.banner)
        layout.addSpacing(10)

        # --- INPUTS SCANNER ---
        layout.addWidget(QLabel("TARGET IP / HOSTNAME", objectName="label_txt"))
        self.f_ip = QFrame(); self.f_ip.setProperty("class", "InputFrame")
        lay_ip = QHBoxLayout(self.f_ip); lay_ip.setContentsMargins(5,0,5,0)
        self.ip_input = QLineEdit(placeholderText="e.g. 192.168.1.1 or example.com")
        lay_ip.addWidget(self.ip_input)
        layout.addWidget(self.f_ip)

        layout.addWidget(QLabel("PORT RANGE", objectName="label_txt"))
        self.f_range = QFrame(); self.f_range.setProperty("class", "InputFrame")
        lay_range = QHBoxLayout(self.f_range); lay_range.setContentsMargins(5,0,5,0)
        self.range_input = QLineEdit(placeholderText="e.g. 20-1000")
        lay_range.addWidget(self.range_input)
        layout.addWidget(self.f_range)

        self.btn_scan = QPushButton("INITIALIZE TCP SCAN", objectName="main_btn")
        self.btn_scan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_scan.clicked.connect(self.start_scan)
        layout.addWidget(self.btn_scan)

        self.console = QTextEdit(readOnly=True)
        layout.addWidget(self.console)
        layout.addSpacing(15)

        # --- SECCION FIREWALL ---
        fw_box = QFrame()
        fw_box.setStyleSheet("background: #0a0505; border: 1px solid #3d0a0a; border-radius: 8px;")
        fw_lay = QVBoxLayout(fw_box)
        
        fw_lay.addWidget(QLabel("DEFENSIVE MEASURES (LINUX IPTABLES)", styleSheet="color: #ff4444; font-size: 11px; font-weight: 900;"))
        f_fire = QHBoxLayout()
        self.port_close = QLineEdit(placeholderText="Port to block...")
        self.port_close.setStyleSheet("background: #000; border: 1px solid #333; color: white; border-radius: 4px; padding: 10px;")
        self.btn_fire = QPushButton("ENFORCE DROP RULE", objectName="firewall_btn")
        self.btn_fire.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_fire.clicked.connect(self.block_port)
        
        f_fire.addWidget(self.port_close); f_fire.addWidget(self.btn_fire)
        fw_lay.addLayout(f_fire)
        layout.addWidget(fw_box)

    def log(self, p, s):
        self.console.append(f"<span style='color:#555;'>[+] PORT </span><span style='color:white; font-weight:bold;'>{p}</span> <span style='color:#A020F0;'>➔</span> <span style='color:#00ff00;'>{s}</span>")

    def start_scan(self):
        target = self.ip_input.text().strip()
        rango = self.range_input.text().strip()
        if not target or "-" not in rango: 
            self.console.append("<span style='color:red;'>[!] Invalid target or range format.</span>")
            return

        try:
            ip_val = socket.gethostbyname(target)
            start, end = map(int, rango.split('-'))
            self.console.clear()
            self.console.append(f"<i style='color:#888;'>Target locked: {ip_val}</i><br>")
            self.btn_scan.setEnabled(False)
            
            self.worker = ScannerWorker(ip_val, start, end)
            self.worker.resultado.connect(self.log)
            self.worker.finalizado.connect(lambda: [self.btn_scan.setEnabled(True), self.console.append("<br><b style='color:#A020F0;'>[✓] SCAN CYCLE COMPLETE.</b>")])
            self.worker.start()
        except Exception as e:
            self.console.append(f"<span style='color:red;'>[!] Resolution Error: {e}</span>")

    def block_port(self):
        p = self.port_close.text().strip()
        if p:
            try:
                subprocess.run(["sudo", "iptables", "-A", "INPUT", "-p", "tcp", "--dport", p, "-j", "DROP"], check=True)
                self.console.append(f"<br><span style='color:#ff4444; font-weight:bold;'>[!] CRITICAL: TCP Port {p} DROPPED at firewall level.</span>")
            except:
                self.console.append("<br><span style='color:orange;'>[!] Action Denied: Root (sudo) privileges required for iptables.</span>")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PortScannerZen()
    win.show()
    sys.exit(app.exec())
