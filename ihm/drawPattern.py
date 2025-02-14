from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QGraphicsScene, QGraphicsView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor, QPainter
import numpy as np
from utils.tools import Tools  # Import de Tools

DEFAULT_PATTERN = "DEFAULT"

class DrawPatternDialog(QDialog):
    def __init__(self, pattern_id=DEFAULT_PATTERN):
        super().__init__()
        self.tools = Tools()  # Instance de Tools pour gérer les patterns
        self.pattern_name = pattern_id  # Nom du pattern chargé

        self.setWindowTitle(f"Dessinez votre pattern ({self.pattern_name})")
        self.setFixedSize(400, 400)

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

        # Stocke les points du dessin
        self.points = []

        # Boutons
        btn_layout = QHBoxLayout()
        
        # Premier groupe de boutons (dessin)
        draw_btn_layout = QHBoxLayout()
        #self.btn_redraw = QPushButton("🔄 Re-dessiner")
        self.btn_clear = QPushButton("🗑️ Effacer")
        self.btn_load_default = QPushButton("📄 Charger Default")
        
        #draw_btn_layout.addWidget(self.btn_redraw)
        draw_btn_layout.addWidget(self.btn_clear)
        draw_btn_layout.addWidget(self.btn_load_default)
        
        # Deuxième groupe de boutons (actions)
        action_btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("💾 Sauvegarder")
        self.btn_close = QPushButton("❌ Fermer")
        
        action_btn_layout.addWidget(self.btn_save)
        action_btn_layout.addWidget(self.btn_close)

        # Ajouter les deux groupes de boutons au layout principal
        layout.addLayout(draw_btn_layout)
        layout.addLayout(action_btn_layout)
        
        self.setLayout(layout)

        # Connexion des boutons
        #self.btn_redraw.clicked.connect(self.redraw_pattern)
        self.btn_clear.clicked.connect(self.clear_pattern)
        self.btn_load_default.clicked.connect(self.load_default_pattern)
        self.btn_save.clicked.connect(self.save_pattern)
        self.btn_close.clicked.connect(self.close)

        # Gestion de la souris
        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)
        self.drawing = False

        # Charger le pattern existant
        self.load_pattern()

    def eventFilter(self, source, event):
        """Gestion des événements souris pour dessiner."""
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
        """Dessine un point et l'ajoute à la liste."""
        pen = QPen(QColor(0, 0, 0), 3)  # Noir, épaisseur 3
        self.scene.addEllipse(pos.x(), pos.y(), 2, 2, pen)
        self.points.append([int(pos.x()), int(pos.y())])  # Ajout sous format (x, y) int

    def redraw_pattern(self):
        """Efface le dessin."""
        self.scene.clear()
        self.points.clear()

    def clear_pattern(self):
        """Efface le dessin actuel."""
        self.scene.clear()
        self.points.clear()
        self.label.setText("✨ Dessin effacé")

    def load_default_pattern(self):
        """Charge le pattern par défaut."""
        try:
            default_pattern = self.tools.get_pattern(DEFAULT_PATTERN)
            if default_pattern and "motif" in default_pattern:
                self.scene.clear()
                self.points = default_pattern["motif"]
                pen = QPen(QColor(0, 0, 0), 3)
                for x, y in self.points:
                    self.scene.addEllipse(x, y, 2, 2, pen)
                print(f"✅ Pattern DEFAULT chargé !")
                self.label.setText(f"✅ Pattern DEFAULT chargé ({len(self.points)} points)")
            else:
                print("❌ Pattern DEFAULT non trouvé ou invalide")
                self.label.setText("❌ Pattern DEFAULT non trouvé")
        except Exception as e:
            print(f"❌ Erreur lors du chargement du pattern DEFAULT : {e}")
            self.label.setText("❌ Erreur de chargement")

    def save_pattern(self):
        """Sauvegarde le pattern avec son nom via Tools."""
        try:
            self.tools.set_pattern(self.pattern_name, motif=self.points)
            print(f"✅ Pattern '{self.pattern_name}' sauvegardé !")
            self.label.setText(f"✅ {len(self.points)} points enregistrés !")
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde : {e}")

    def load_pattern(self):
        """Charge un pattern existant via Tools."""
        try:
            pattern = self.tools.get_pattern(self.pattern_name)
            if pattern and "motif" in pattern:
                self.points = pattern["motif"]
                pen = QPen(QColor(0, 0, 0), 3)
                for x, y in self.points:
                    self.scene.addEllipse(x, y, 2, 2, pen)
                print(f"✅ Pattern '{self.pattern_name}' chargé !")
                if self.pattern_name == "DEFAULT":
                    self.label.setText(f"✅ Pattern DEFAULT chargé ({len(self.points)} points)")
                else:
                    self.label.setText(f"✅ {len(self.points)} points chargés !")
            else:
                print(f"ℹ️ Aucun pattern trouvé pour '{self.pattern_name}', dessin vide.")
        except Exception as e:
            print(f"❌ Erreur lors du chargement : {e}")

    def get_numpy_contour(self):
        """Retourne le contour dessiné sous forme de tableau NumPy pour OpenCV."""
        if self.points:
            return np.array(self.points, dtype=np.int32).reshape((-1, 1, 2))
        return None

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    window2 = DrawPatternDialog()  # Charger DEFAULT_PATTERN
    window2.exec_()

    # Exemple d'export NumPy
    contour_np = window2.get_numpy_contour()
    if contour_np is not None:
        print("🔹 Contour NumPy prêt pour OpenCV:", contour_np.shape)
