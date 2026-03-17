import sys
import os
from pytube import YouTube
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QTextEdit, QLabel, QFrame, QPushButton, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon

class YoutubePytubeUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("VantXploit - Media Downloader")
        self.setFixedSize(650, 700)
        
        self.setStyleSheet("""
            QWidget { background-color: #050508; color: #ffffff; font-family: 'Segoe UI', sans-serif; }
            .InputFrame { background-color: #0d0d12; border: 1px solid #1c1c24; border-radius: 8px; margin-bottom: 10px; padding: 5px; }
            .InputFrame:focus-within { border: 1px solid #A020F0; }
            QLineEdit { background-color: transparent; border: none; color: white; font-size: 14px; padding: 5px; }
            QPushButton#main_btn { background-color: #1a0b2e; border: 1px solid #A020F0; border-radius: 6px; color: white; padding: 15px; font-weight: 900; font-size: 13px; letter-spacing: 1px;}
            QPushButton#main_btn:hover { background-color: #A020F0; }
            QPushButton#browse_btn { background-color: #1a1a24; border: 1px solid #333; border-radius: 5px; color: #ccc; padding: 8px 15px; font-weight: bold; }
            QPushButton#browse_btn:hover { background-color: #333; }
            QTextEdit { background-color: #08080a; border: 1px solid #1c1c24; border-radius: 8px; color: #e0e0e0; font-family: 'Consolas', monospace; padding: 15px; }
            QLabel#label_txt { color: #888; font-size: 11px; font-weight: bold; margin-bottom: 2px; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        # --- BANNER ---
        self.banner = QLabel()
        ruta_banner = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "banner.jpg")
        if os.path.exists(ruta_banner):
            self.banner.setPixmap(QPixmap(ruta_banner).scaled(590, 110, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.banner.setText("[ ASSETS/BANNER.JPG NOT FOUND ]")
            self.banner.setStyleSheet("background: #111; color: #555; font-weight: bold;")
            self.banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.banner.setFixedHeight(110)
        layout.addWidget(self.banner)
        layout.addSpacing(10)

        # --- INPUTS ---
        layout.addWidget(QLabel("TARGET URL", objectName="label_txt"))
        self.frame_url = QFrame(); self.frame_url.setProperty("class", "InputFrame")
        lay_url = QHBoxLayout(self.frame_url); lay_url.setContentsMargins(5,0,5,0)
        self.url_input = QLineEdit(); self.url_input.setPlaceholderText("https://youtube.com/watch?v=...")
        lay_url.addWidget(self.url_input)
        layout.addWidget(self.frame_url)

        layout.addWidget(QLabel("OUTPUT FILENAME", objectName="label_txt"))
        self.frame_name = QFrame(); self.frame_name.setProperty("class", "InputFrame")
        lay_name = QHBoxLayout(self.frame_name); lay_name.setContentsMargins(5,0,5,0)
        self.name_input = QLineEdit(); self.name_input.setPlaceholderText("video_name (without .mp4)")
        lay_name.addWidget(self.name_input)
        layout.addWidget(self.frame_name)

        layout.addWidget(QLabel("SAVE DIRECTORY", objectName="label_txt"))
        self.frame_path = QFrame(); self.frame_path.setProperty("class", "InputFrame")
        lay_path = QHBoxLayout(self.frame_path); lay_path.setContentsMargins(5,0,5,0)
        self.path_input = QLineEdit(); self.path_input.setPlaceholderText("C:/Users/.../Downloads")
        self.btn_browse = QPushButton("BROWSE", objectName="browse_btn")
        self.btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_browse.clicked.connect(self.seleccionar_carpeta)
        lay_path.addWidget(self.path_input); lay_path.addWidget(self.btn_browse)
        layout.addWidget(self.frame_path)

        layout.addSpacing(10)
        self.btn_download = QPushButton("EXECUTE MEDIA EXTRACTION", objectName="main_btn")
        self.btn_download.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_download.clicked.connect(self.descargar_pytube)
        layout.addWidget(self.btn_download)

        self.console = QTextEdit(); self.console.setReadOnly(True)
        layout.addWidget(self.console)

    def seleccionar_carpeta(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder: self.path_input.setText(folder)

    def log(self, text, is_error=False):
        color = "#ff4444" if is_error else "#A020F0"
        self.console.append(f"<span style='color:{color};'>[+] {text}</span>")
        QApplication.processEvents()

    def descargar_pytube(self):
        url = self.url_input.text().strip()
        path = self.path_input.text().strip()
        name = self.name_input.text().strip()

        if not url or not path:
            self.log("Missing required parameters (URL or Path).", True)
            return

        try:
            self.console.clear()
            self.log("Establishing connection to stream provider...")
            yt = YouTube(url)
            video = yt.streams.get_highest_resolution()
            self.log(f"Target locked: {yt.title}")
            self.log("Downloading... please wait.")
            
            out_file = video.download(output_path=path)
            
            if name:
                new_file = os.path.join(path, f"{name}.mp4")
                os.rename(out_file, new_file)
                self.log(f"Saved to disk as: {name}.mp4")
            else:
                self.log("Extraction completed successfully.")

        except Exception as e:
            self.log(f"Extraction Failed: {str(e)}", True)
            self.log("Note: Pytube blocks are common. Consider yt-dlp module if persistent.", "#888")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = YoutubePytubeUI()
    win.show()
    sys.exit(app.exec())
