import sys
import os
import time
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QTextEdit, QLabel, QFrame, QComboBox)
from PyQt6.QtCore import Qt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from deep_translator import GoogleTranslator

class EmailFootprintUI(QWidget):
    def __init__(self):
        super().__init__()
        self.driver = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("VantXploit - Email Tracker")
        self.setFixedSize(650, 650)
        
        self.setStyleSheet("""
            QWidget { background-color: #050508; color: #ffffff; font-family: 'Segoe UI', sans-serif; }
            #input_frame { background-color: #0d0d12; border: 1px solid #2a1b3d; border-radius: 8px; min-height: 48px; }
            #input_frame:focus-within { border: 1px solid #A020F0; }
            QLineEdit { background-color: transparent; border: none; color: #ffffff; font-size: 14px; padding: 5px;}
            QComboBox { background-color: #0d0d12; border: 1px solid #2a1b3d; color: white; border-radius: 6px; padding: 8px; min-width: 180px; }
            QComboBox:focus { border: 1px solid #A020F0; }
            QTextEdit { background-color: #08080a; border: 1px solid #1c1c24; border-radius: 8px; color: #e0e0e0; font-family: 'Consolas', monospace; padding: 15px; }
            QLabel#header { font-size: 24px; font-weight: 900; color: white; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 20)
        layout.setSpacing(15)

        layout.addWidget(QLabel("EMAIL FOOTPRINT", objectName="header"))

        nav_lay = QHBoxLayout()
        lbl_browser = QLabel("Browser Engine:")
        lbl_browser.setStyleSheet("color: #A020F0; font-weight: bold;")
        nav_lay.addWidget(lbl_browser)
        
        self.browser_choice = QComboBox()
        self.browser_choice.addItem("Chrome (Visible)")
        self.browser_choice.addItem("Chrome (Headless - Stealth)")
        nav_lay.addWidget(self.browser_choice)
        nav_lay.addStretch()
        layout.addLayout(nav_lay)

        self.input_frame = QFrame(objectName="input_frame")
        input_inner = QHBoxLayout(self.input_frame)
        input_inner.setContentsMargins(15, 0, 15, 0)
        
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Target Email Address... [Press Enter]")
        self.input_email.returnPressed.connect(self.ejecutar_rastro)
        input_inner.addWidget(self.input_email)
        layout.addWidget(self.input_frame)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        layout.addWidget(self.console)

        credits = QLabel("VantXploit OSINT Module")
        credits.setStyleSheet("color: #444; font-size: 11px; font-weight: bold;")
        layout.addWidget(credits, alignment=Qt.AlignmentFlag.AlignRight)

    def log(self, text, color="white"):
        self.console.append(f"<span style='color:{color};'>{text}</span>")
        QApplication.processEvents()

    def check_site(self, nombre, url, selector_type, selector_val, email, keyword_found):
        self.log(f"<span style='color:#555;'>[~] Probing {nombre}...</span>")
        try:
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 10)
            campo = wait.until(EC.presence_of_element_located((selector_type, selector_val)))
            campo.send_keys(email)
            campo.send_keys(Keys.RETURN)
            time.sleep(8)
            
            page_text = self.driver.execute_script("return document.documentElement.innerText")
            translated = GoogleTranslator(source='auto', target='en').translate(page_text)
            
            if keyword_found.lower() in translated.lower():
                self.log(f"[+] {nombre}: <b style='color:#00ff00;'>REGISTERED</b>")
            else:
                self.log(f"[-] {nombre}: Not registered")
        except Exception:
            self.log(f"[!] {nombre}: <span style='color:#ffaa00;'>Timeout / Blocked</span>")

    def ejecutar_rastro(self):
        email = self.input_email.text().strip()
        if not email: return
        
        self.console.clear()
        self.log(f"<b style='color:#A020F0;'>[>] INITIALIZING TRACE FOR:</b> {email}<br>")

        opts = webdriver.ChromeOptions()
        if "Headless" in self.browser_choice.currentText():
            opts.add_argument("--headless")
        
        try:
            self.driver = webdriver.Chrome(options=opts)
            sitios = [
                ("Google", "https://accounts.google.com/signin/v2/identifier", By.NAME, "identifier", "Enter your password"),
                ("Instagram", "https://www.instagram.com/accounts/emailsignup/", By.NAME, "emailOrPhone", "Another account uses"),
                ("Microsoft", "https://login.microsoftonline.com/", By.NAME, "loginfmt", "Enter password"),
                ("Snapchat", "https://accounts.snapchat.com/", By.ID, "ai_input", "Confirm it's you")
            ]

            for s in sitios:
                self.check_site(s[0], s[1], s[2], s[3], email, s[4])

            self.driver.quit()
            self.log("<br><b style='color:#A020F0;'>[✓] TRACE COMPLETE.</b>")
            
        except Exception as e:
            self.log(f"<br><b style='color:#ff4444;'>[X] CRITICAL ERROR:</b> {e}")
            if self.driver: self.driver.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmailFootprintUI()
    window.show()
    sys.exit(app.exec())
