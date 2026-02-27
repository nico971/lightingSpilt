from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel, QHBoxLayout,
    QGraphicsScene, QGraphicsView, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor, QPainter
import numpy as np
import cv2
import pymupdf
from utils.tools import Tools
from ihm.color_calibration_dialog import ColorCalibrationDialog  # version complète intégrée

DEFAULT_PATTERN = "DEFAULT"

class DrawPatternDialog(QDialog):
    def __init__(self, pattern_id=DEFAULT_PATTERN):
        super().__init__()
        self.tools = Tools()
        self.pattern_name = pattern_id
        self.setWindowTitle(f"Dessinez votre pattern ({self.pattern_name})")
        self.setFixedSize(420, 480)

        layout = QVBoxLayout()

        # Label d'information
        self.label = QLabel(f"Dessinez votre pattern: {self.pattern_name}", self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # Zone de dessin
        self.scene = QGraphicsScene(0, 0, 300, 300)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        layout.addWidget(self.view)

        self.points = []
        # valeurs HSV par défaut
        self.color_range = {
            "lower": [0, 48, 0],
            "upper": [179, 255, 255]
        }

        # Boutons principaux
        btn_layout = QHBoxLayout()
        self.btn_clear = QPushButton("🗑️ Effacer")
        self.btn_load_default = QPushButton("📄 Charger Default")
        self.btn_calibrate_detection = QPushButton("⚙️Color")
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.btn_load_default)
        btn_layout.addWidget(self.btn_calibrate_detection)
        layout.addLayout(btn_layout)

        # Boutons actions
        action_btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("💾 Sauvegarder")
        self.btn_close = QPushButton("❌ Fermer")
        action_btn_layout.addWidget(self.btn_save)
        action_btn_layout.addWidget(self.btn_close)
        layout.addLayout(action_btn_layout)

        self.setLayout(layout)

        # Connexions
        self.btn_clear.clicked.connect(self.clear_pattern)
        self.btn_load_default.clicked.connect(self.load_default_pattern)
        self.btn_calibrate_detection.clicked.connect(self.calibrate_detection)
        self.btn_save.clicked.connect(self.save_pattern)
        self.btn_close.clicked.connect(self.close)

        # Gestion souris
        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)
        self.drawing = False

        # Charger pattern si existant
        self.load_pattern()

    # --- Dessin ---
    def eventFilter(self, source, event):
        if source == self.view.viewport():
            if event.type() == event.MouseButtonPress and event.button() == Qt.LeftButton:
                self.drawing = True
                return True
            elif event.type() == event.MouseMove and self.drawing:
                pos = self.view.mapToScene(event.pos())
                self.draw_point(pos)
                return True
            elif event.type() == event.MouseButtonRelease and event.button() == Qt.LeftButton:
                self.drawing = False
                return True
        return super().eventFilter(source, event)

    def draw_point(self, pos):
        pen = QPen(QColor(0, 0, 0), 3)
        self.scene.addEllipse(pos.x(), pos.y(), 2, 2, pen)
        self.points.append([int(pos.x()), int(pos.y())])

    # --- Actions ---
    def clear_pattern(self):
        self.scene.clear()
        self.points.clear()
        self.label.setText("✨ Dessin effacé")

    def load_default_pattern(self):
        default_pattern = self.tools.get_pattern(DEFAULT_PATTERN)
        if default_pattern and "motif" in default_pattern:
            self.scene.clear()
            self.points = default_pattern["motif"]
            pen = QPen(QColor(0, 0, 0), 3)
            for x, y in self.points:
                self.scene.addEllipse(x, y, 2, 2, pen)
            # charger HSV si existant
            self.color_range = default_pattern.get("color_range", self.color_range)
            self.label.setText(f"✅ Pattern DEFAULT chargé ({len(self.points)} points) avec HSV")
        else:
            self.label.setText("❌ Aucun pattern par défaut trouvé")

    def calibrate_detection(self):
        """Calibrage HSV via ColorCalibrationDialog complet"""
        pdf_path, _ = QFileDialog.getOpenFileName(self, "Choisir un PDF", "", "PDF Files (*.pdf)")
        if not pdf_path:
            return
        try:
            dialog = ColorCalibrationDialog(pdf_path=pdf_path, page_number=0,lower=self.color_range.get("lower", None),upper=self.color_range.get("upper", None))
            if dialog.exec_():
                lower, upper = dialog.get_range()
                self.color_range = {
                    "lower": [int(x) for x in lower],
                    "upper": [int(x) for x in upper]
                }
                self.label.setText(f"✅ HSV calibré: {lower} → {upper}")
                print(f"✅ HSV sauvegardé: lower={lower}, upper={upper}")
        except Exception as e:
            print(f"❌ Erreur calibrage HSV : {e}")

    def save_pattern(self):
        try:
            # sauvegarde motif + HSV
            self.tools.set_pattern(
                self.pattern_name,
                motif=self.points,
                color_range=self.color_range
            )
            self.label.setText(f"✅ Pattern sauvegardé ({len(self.points)} pts, couleur HSV incluse)")
            print(f"✅ Pattern '{self.pattern_name}' sauvegardé avec HSV {self.color_range}")
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde : {e}")

    def load_pattern(self):
        pattern = self.tools.get_pattern(self.pattern_name)
        if pattern:
            self.points = pattern.get("motif", [])
            self.color_range = pattern.get("color_range", self.color_range)  # récupère HSV
            pen = QPen(QColor(0, 0, 0), 3)
            for x, y in self.points:
                self.scene.addEllipse(x, y, 2, 2, pen)
            self.label.setText(f"✅ Pattern chargé ({len(self.points)} pts) avec HSV")
        else:
            self.label.setText("ℹ️ Aucun pattern trouvé")

    def get_numpy_contour(self):
        if self.points:
            return np.array(self.points, dtype=np.int32).reshape((-1, 1, 2))
        return None
