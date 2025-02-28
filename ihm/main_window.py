import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel,
    QGraphicsOpacityEffect, QMenu, QAction, QSystemTrayIcon, QApplication,QMessageBox
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QFont, QIcon
from .menu import create_menu
from .watcher_table import WatcherTable
from utils.tools import Tools
from threads.pdf_processor_thread import PDFProcessorThread
from .modal_Info import NotificationModal
from watchers.watcher_manager import WatcherManager

class PDFWatcherApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.icon_path = os.path.join(os.path.dirname(__file__), 'ico.png')
        self.saved_geometry = None  # Variable pour stocker la géométrie
        self.saved_state = None  # Variable pour stocker l'état de la fenêtre
        self.init_ui()
        self.init_tray_icon()
        self.app_closing = False  # Flag pour savoir si l'application se ferme ou passe en arrière-plan

    def init_ui(self):
        """Initialisation de l'IHM."""
        self.setWindowIcon(QIcon(self.icon_path))
        self.setWindowTitle("📂 PDF Splitter - Gestion Multi-Dossiers")
        self.setGeometry(200, 200, 900, 450)  # Position par défaut
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
        self.watcher_table.load_watchers_from_json()

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

    def init_tray_icon(self):
        """Initialise l'icône du System Tray."""

        self.tray_icon = QSystemTrayIcon(QIcon(self.icon_path), self)
        self.tray_icon.setToolTip("PDF Splitter - Gestion Multi-Dossiers")

        # Création du menu du System Tray
        self.tray_menu = QMenu()

        # Action pour rouvrir la fenêtre
        open_action = QAction("Ouvrir", self)
        open_action.triggered.connect(self.show_window)
        self.tray_menu.addAction(open_action)

        # Action pour quitter
        exit_action = QAction("Quitter", self)
        exit_action.triggered.connect(self.quit_app)
        self.tray_menu.addAction(exit_action)

        # Associer le menu à l'icône du systray
        self.tray_icon.setContextMenu(self.tray_menu)

        # Afficher l'icône dans la barre des tâches
        self.tray_icon.show()

        # Connecter l'événement de clic sur l'icône du systray
        self.tray_icon.activated.connect(self.on_tray_icon_click)

    def closeEvent(self, event):
        """Intercepte la fermeture pour masquer la fenêtre ou quitter l'application."""
        watch = WatcherManager()
        encours = watch.are_watchers_running()  # Vérifie si des watchers sont actifs

        if self.app_closing:  # Si on veut quitter définitivement
            if encours:
                reply = QMessageBox.question(
                    self,
                    "Confirmation",
                    "Il y a des watchers en cours. Voulez-vous vraiment quitter ?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.tray_icon.hide()  # Cacher l'icône du systray
                    event.accept()  # Autorise la fermeture
                    QApplication.quit()  # Quitte proprement
                else:
                    event.ignore()  # Annule la fermeture
                    self.app_closing = False  # Réinitialise l'état
            else:
                self.tray_icon.hide()  # Cacher l'icône du systray
                event.accept()  # Autorise la fermeture
                QApplication.quit()  # Quitte proprement

        else:  # Si on ne veut pas quitter, on minimise l'application en arrière-plan
            event.ignore()
            NotificationModal("Je travaille en arrière-plan !!", type_="Info", duration=3000, parent=self).exec_()
            self.saved_geometry = self.geometry()  # Sauvegarde la position actuelle
            self.saved_state = self.windowState()  # Sauvegarde l'état (normal/maximisé)
            self.hide()  # Masquer la fenêtre principale
            self.tray_icon.showMessage(
                "PDF Splitter",
                "L'application continue à tourner en arrière-plan.",
                QSystemTrayIcon.Information,
                2000
            )

    def minimize_to_tray(self):
        """Minimise l'application dans la barre des tâches (System Tray)."""
        NotificationModal("Je travaille en arrière-plan !!", type_="Info", duration=2000, parent=self).exec_()
        self.saved_geometry = self.geometry()  # Enregistre la taille et position
        self.saved_state = self.windowState()  # Enregistre l'état (maximisé, normal)
        self.hide()
        self.tray_icon.showMessage(
            "PDF Splitter",
            "L'application continue à tourner en arrière-plan.",
            QSystemTrayIcon.Information,
            2000
        )

    def on_tray_icon_click(self, reason):
        """Événement déclenché lorsqu'on clique sur l'icône du systray."""
        if reason == QSystemTrayIcon.Trigger:  # Si un clic simple est effectué
            self.show_window()

    def show_window(self):
        """Afficher la fenêtre principale avec animation fluide."""
        self.showNormal()

        if self.saved_geometry:  # Si une géométrie a été sauvegardée
            self.setGeometry(self.saved_geometry)  # Restaurer la géométrie
            self.setWindowState(self.saved_state)  # Restaurer l'état de la fenêtre (normal/maximisé)

        self.activateWindow()

    def quit_app(self):
        """Quitte proprement l'application en passant par closeEvent."""
        self.app_closing = True  # Indiquer que l'on veut quitter définitivement
        self.close()  # Déclenche closeEvent()

