from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QIcon
from .menu import create_menu
from .watcher_table import WatcherTable
from utils.tools import Tools
from threads.pdf_processor_thread import PDFProcessorThread

class PDFWatcherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialisation de l'IHM."""

        self.setWindowIcon(QIcon("ico.png"))
        self.setWindowTitle("📂 PDF Splitter - Gestion Multi-Dossiers")
        self.setGeometry(200, 200, 900, 450)
        self.setStyleSheet(self.load_stylesheet())

        self.create_menu()
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Titre
        self.title_label = QLabel("📂 PDF Splitter - Multi-Dossier")
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: #F0F0F0; margin-bottom: 10px;")
        layout.addWidget(self.title_label)

        # Table des watchers
        self.watcher_table = WatcherTable(self)
        layout.addWidget(self.watcher_table)
        
        # Bouton pour ajouter un watcher
        self.btn_add_watcher = QPushButton("➕ Ajouter un dossier à surveiller")
        layout.addWidget(self.btn_add_watcher)
        self.setCentralWidget(central_widget)
        self.btn_add_watcher.clicked.connect(lambda: self.watcher_table.add_watcher(save=True))
        # Animation d’ouverture
        self.fade_in()
        self.watcher_table.load_watchers_from_json("C:\\Users\\Nicolas\\Documents\\Developpement\\Simpac_python\\lightingSpilt\\assets\\patterns.json")

        #

    def create_menu(self):
        """Création du menu."""
        create_menu(self)

    def load_stylesheet(self):
        """Charge le style global."""
        return """
            QWidget {
                background-color: #222;
                color: #F0F0F0;
                font-size: 14px;
            }
            QPushButton {
                background-color: #5A98FF;
                color: white;
                border-radius: 8px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5A85D6;
            }
        """
    def fade_in(self):
        """Anime l'ouverture de la fenêtre avec un fondu."""
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(800)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()