from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QGraphicsOpacityEffect, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont

class NotificationModal(QDialog):
    def __init__(self, message, type_="Info", duration=None, parent=None):
        """
        Fenêtre modale de notification.

        :param message: Texte à afficher
        :param type_: Type de notification (Info, Warning, Error, Success)
        :param duration: Temps avant fermeture automatique (ms), None pour désactiver l'auto-fermeture
        """
        super().__init__(parent)
        #self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setWindowTitle(type_)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)

        self.message = message
        self.type_ = type_
        self.duration = duration

        self.init_ui()
        self.fade_in()

        if self.duration:  # Si duration est défini, on programme la fermeture automatique
            QTimer.singleShot(self.duration, self.fade_out)

    def init_ui(self):
        """Initialisation de l'interface de la notification."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Définition des couleurs par type
        colors = {
            "Info": "#5A98FF",
            "Warning": "#FFA500",
            "Error": "#FF5555",
            "Success": "#28A745"
        }
        bg_color = colors.get(self.type_, "#5A98FF")  # Default: Info

        # Style du widget
        self.setStyleSheet(f"""
            background-color: {bg_color};
            color: white;
            border-radius: 10px;
            padding: 10px;
            font-size: 14px;
        """)

        # Label du message
        self.label = QLabel(self.message)
        self.label.setFont(QFont("Arial", 12, QFont.Bold))
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # Bouton de fermeture
        self.btn_close = QPushButton("X")
        self.btn_close.setFixedSize(20, 20)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                color: #DDDDDD;
            }
        """)
        self.btn_close.clicked.connect(self.fade_out)  # Connexion au fade_out

        # Définition de la taille et de la position
        self.setFixedSize(300, 100)
        parent_geometry = self.parent().geometry() if self.parent() else None
        if parent_geometry:
            self.move(
                parent_geometry.x() + parent_geometry.width() // 2 - self.width() // 2,
                parent_geometry.y() + 50
            )

    def fade_in(self):
        """Anime l'apparition en fondu."""
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()

    def fade_out(self):
        """Anime la disparition en fondu et ferme la fenêtre."""
        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.finished.connect(self.close)  # Ferme la fenêtre après l'animation
        self.animation.start()
