import sys
import numpy as np
import fitz  # pymupdf
import cv2
from PyQt5.QtWidgets import (
    QApplication, QDialog, QLabel, QVBoxLayout, QHBoxLayout,
    QSlider, QPushButton, QGridLayout, QSizePolicy, QMessageBox,
    QMainWindow, QAction
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QFont

# --- Dialog principal ---
class ColorCalibrationDialog(QDialog):
    def __init__(self, parent=None, pdf_path="test.pdf", page_number=0, lower=(21, 60, 90), upper=(48, 255, 255)):
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.page_number = page_number
        self.num_pages = self.doc.page_count
        self.lower = np.array(lower, dtype=np.uint8)
        self.upper = np.array(upper, dtype=np.uint8)

        self.setWindowTitle("Calibration HSV PDF - Top Right")
        self.resize(950, 700)

        main_layout = QVBoxLayout()

        # --- Vue originale et masque ---
        view_layout = QHBoxLayout()
        self.label_original = QLabel()
        view_layout.addWidget(self.label_original)
        self.label_masked = QLabel()
        view_layout.addWidget(self.label_masked)
        main_layout.addLayout(view_layout)

        # --- Presets ---
        self.presets_layout = QHBoxLayout()
        self.presets = [
            ("🟡 Jaune fluo", (21, 60, 90), (48, 255, 255)),
            ("🟢 Vert fluo", (35, 80, 100), (90, 255, 255)),
            ("💗 Rose", (140, 50, 100), (179, 255, 255)),
            ("🔵 Bleu", (90, 80, 100), (130, 255, 255)),
            ("All_color", (0, 48, 0), (179, 255, 255))
        ]
        for label, low, high in self.presets:
            btn = QPushButton(label)
            if label == "All_color":
                # bouton blanc
                btn.setStyleSheet(
                    "background-color: white; color: black; font-weight: bold; border-radius: 6px; padding: 5px;"
                )
            else:
                # boutons colorés pour les autres presets
                btn.setStyleSheet(
                    f"background-color: rgb({self.hsv_to_rgb_css(low, high)}); "
                    "color: black; font-weight: bold; border-radius: 6px; padding: 5px;"
                )
            btn.clicked.connect(lambda _, lo=low, hi=high: self.apply_preset(lo, hi))
            self.presets_layout.addWidget(btn)
        main_layout.addLayout(self.presets_layout)

        # --- Bandeau couleur ---
        self.color_band = QLabel()
        self.color_band.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.color_band.setMinimumHeight(35)
        self.color_band.setMaximumHeight(35)
        self.color_band.setStyleSheet("border: 1px solid #888; border-radius: 4px;")
        self.color_band.setScaledContents(True)
        main_layout.addWidget(self.color_band)

        # --- Texte sous bandeau ---
        self.label_text = QLabel("Calibrate")
        self.label_text.setAlignment(Qt.AlignCenter)
        self.label_text.setFont(QFont("Arial", 12, QFont.Bold))
        main_layout.addWidget(self.label_text)

        # --- Sliders ---
        grid = QGridLayout()
        self.sliders = {}
        self.slider_labels = {}
        labels = ["Couleur", "Saturation", "Luminosité", "Couleur Max", "Saturation Max", "Luminosité Max"]
        defaults = [*self.lower, *self.upper]
        ranges = [179, 255, 255, 179, 255, 255]

        for i, (name, val, max_val) in enumerate(zip(labels, defaults, ranges)):
            lbl = QLabel(name)
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(max_val)
            slider.setValue(int(val))
            value_label = QLabel(str(val))
            slider.valueChanged.connect(self.update_mask)
            slider.valueChanged.connect(lambda v, l=value_label: l.setText(str(v)))
            grid.addWidget(lbl, i, 0)
            grid.addWidget(slider, i, 1)
            grid.addWidget(value_label, i, 2)
            self.sliders[name] = slider
            self.slider_labels[name] = value_label
        main_layout.addLayout(grid)

        # --- Navigation ---
        nav_layout = QHBoxLayout()
        self.btn_prev = QPushButton("⬅️ Précédent")
        self.btn_next = QPushButton("➡️ Suivant")
        self.label_page = QLabel(f"Page : {self.page_number + 1} / {self.num_pages}")
        nav_layout.addWidget(self.btn_prev)
        nav_layout.addWidget(self.label_page)
        nav_layout.addWidget(self.btn_next)
        main_layout.addLayout(nav_layout)
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)

        # --- Valider / Annuler ---
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("✅ Valider")
        btn_cancel = QPushButton("❌ Annuler")
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        main_layout.addLayout(btn_layout)
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        self.setLayout(main_layout)
        self.load_page()
        self.update_mask()

    # --- Méthodes principales ---
    def update_color_band(self):
        h_min = self.sliders["Couleur"].value()
        s_min = self.sliders["Saturation"].value()
        v_min = self.sliders["Luminosité"].value()
        h_max = self.sliders["Couleur Max"].value()
        s_max = self.sliders["Saturation Max"].value()
        v_max = self.sliders["Luminosité Max"].value()
        h_mean = int((h_min + h_max) / 2)
        s_mean = int((s_min + s_max) / 2)
        v_mean = int((v_min + v_max) / 2)
        color_hsv = np.uint8([[[h_mean, s_mean, v_mean]]])
        color_rgb = cv2.cvtColor(color_hsv, cv2.COLOR_HSV2RGB)[0][0]
        self.color_band.setStyleSheet(
            f"background-color: rgb({color_rgb[0]}, {color_rgb[1]}, {color_rgb[2]});"
            "border: 1px solid #888; border-radius: 4px;"
        )

    def hsv_to_rgb_css(self, low, high):
        h_mean = int((low[0] + high[0]) / 2)
        s_mean = int((low[1] + high[1]) / 2)
        v_mean = int((low[2] + high[2]) / 2)
        color_hsv = np.uint8([[[h_mean, s_mean, v_mean]]])
        color_rgb = cv2.cvtColor(color_hsv, cv2.COLOR_HSV2RGB)[0][0]
        return f"{color_rgb[0]}, {color_rgb[1]}, {color_rgb[2]}"

    def apply_preset(self, low, high):
        names = ["Couleur", "Saturation", "Luminosité", "Couleur Max", "Saturation Max", "Luminosité Max"]
        vals = [*low, *high]
        for name, val in zip(names, vals):
            self.sliders[name].setValue(val)
        self.update_mask()

    def load_page(self):
        self.img_original = self._load_pdf_top_right(self.page_number)
        self.img_display = self.img_original.copy()
        self.label_original.setPixmap(self.cv_to_pixmap(self.img_original))
        self.update_mask()

    def _load_pdf_top_right(self, page_number, clip_size=(100, 100), zoom=2):
        page = self.doc.load_page(page_number)
        mat = fitz.Matrix(zoom, zoom)
        rect = page.rect
        clip_top_right = fitz.Rect(rect.width - clip_size[0], 0, rect.width, clip_size[1])
        pix = page.get_pixmap(alpha=True, dpi=150, matrix=mat, clip=clip_top_right)
        img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if img_np.shape[2] == 4:
            img_np = img_np[:, :, :3]
        return img_np

    def prev_page(self):
        if self.page_number > 0:
            self.page_number -= 1
            self.label_page.setText(f"Page : {self.page_number + 1} / {self.num_pages}")
            self.load_page()

    def next_page(self):
        if self.page_number < self.num_pages - 1:
            self.page_number += 1
            self.label_page.setText(f"Page : {self.page_number + 1} / {self.num_pages}")
            self.load_page()

    def update_mask(self):
        h_min = self.sliders["Couleur"].value()
        s_min = self.sliders["Saturation"].value()
        v_min = self.sliders["Luminosité"].value()
        h_max = self.sliders["Couleur Max"].value()
        s_max = self.sliders["Saturation Max"].value()
        v_max = self.sliders["Luminosité Max"].value()
        self.lower = np.array([h_min, s_min, v_min], dtype=np.uint8)
        self.upper = np.array([h_max, s_max, v_max], dtype=np.uint8)

        hsv = cv2.cvtColor(self.img_original, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv, self.lower, self.upper)
        result = cv2.bitwise_and(self.img_original, self.img_original, mask=mask)
        self.label_masked.setPixmap(self.cv_to_pixmap(result))
        self.update_color_band()

    def cv_to_pixmap(self, img_np):
        h, w, ch = img_np.shape
        bytes_per_line = ch * w
        qimg = QImage(img_np.tobytes(), w, h, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(qimg).scaled(400, int(400 * h / w), Qt.KeepAspectRatio)

    def show_help(self):
        msg = QMessageBox()
        msg.setWindowTitle("Aide à la calibration")
        msg.setText(
            "Cette fenêtre vous permet de calibrer la couleur d'un PDF.\n\n"
            "- Déplacez les sliders pour ajuster Couleur / Saturation / Luminosité.\n"
            "- Les boutons presets appliquent des couleurs prédéfinies.\n"
            "- Le bandeau change selon la couleur sélectionnée.\n"
            "- Les flèches permettent de naviguer entre les pages.\n"
            "- Validez pour enregistrer la calibration."
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def get_range(self):
        return self.lower, self.upper
