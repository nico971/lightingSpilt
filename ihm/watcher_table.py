import time,json
from PyQt5.QtWidgets import (QTableWidget, QTableWidgetItem, QCheckBox, QPushButton, QHBoxLayout, QLabel, QWidget, QFileDialog, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from utils.tools import Tools
#from watchers.watcher import Watcher
from watchers.watcher_manager import WatcherManager

from threads.pdf_processor_thread import PDFProcessorThread  # Assurez-vous que ce fichier existe
from .watcherConfigMenu import WatcherConfigMenu  # Ajouter cet import en haut du fichier


class WatcherTable(QTableWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels(["Source", "Destination", "Automatique", "Statut", "Run", "Delete", "Options"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setStyleSheet(self.table_stylesheet())
        self.watcher_manager = WatcherManager()  # Utilisation du gestionnaire unique


    def table_stylesheet(self):
        """Style pour la table"""
        return """
            QTableWidget {
                background-color: #333;
                gridline-color: #444;
                border: none;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #444;
                color: #F0F0F0;
                padding: 5px;
                border: none;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #444;
            }
        """

    def add_watcher(self, id=False, input_dir=False, output_dir=False, pattern=False, auto=False, save=False):
        """Ajoute un watcher avec ses paramètres dans le tableau."""
        # Si aucun chemin n'est fourni, afficher une boîte de dialogue
        if not input_dir:
            input_dir = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier source")

        if not output_dir:
            output_dir = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier de sortie")

        row_position = self.rowCount()
        self.insertRow(row_position)

        # Générer un ID unique si non fourni
        watcher_id = id if id else f'{row_position}_{int(time.time() * 1000000)}'

        # Ajouter le watcher au WatcherManager
        watcher = self.watcher_manager.add_watcher(watcher_id=watcher_id, input_dir=input_dir, output_dir=output_dir, auto=auto)

        # Stocker l'ID avec Qt.UserRole dans le premier élément
        input_item = self.create_table_item(input_dir)
        input_item.setData(Qt.UserRole, watcher_id)  # Stocke l'ID

        # Ajout des valeurs dans le tableau
        self.setItem(row_position, 0, input_item)
        self.setItem(row_position, 1, self.create_table_item(output_dir))

        # Fusion des cellules pour Auto et Statut dans la colonne "Automatique"
        auto_status_widget = QWidget()
        auto_status_layout = QHBoxLayout()
        auto_checkbox = QCheckBox()
        auto_checkbox.setStyleSheet("margin-left: 15px;")
        status_label = QLabel("OFF")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setStyleSheet("color: #FF5A5A;")

        auto_status_layout.addWidget(auto_checkbox)
        auto_status_layout.addWidget(status_label)
        auto_status_layout.setContentsMargins(0, 0, 0, 0)

        auto_status_widget.setLayout(auto_status_layout)
        self.setCellWidget(row_position, 2, auto_status_widget)

        progress_statut = QLabel("")
        progress_statut.setStyleSheet("color: #FF5A5A;")  # Correction : enlever "align: center;"
        progress_statut.setAlignment(Qt.AlignCenter)  # Ajout : alignement correct
        self.setCellWidget(row_position, 3, progress_statut)

        # Bouton RUN
        btn_run = QPushButton("▶")
        btn_run.setStyleSheet(self.button_style("#5AAF5A", "#85E085"))
        self.setCellWidget(row_position, 4, btn_run)

        # Bouton DELETE
        btn_delete = QPushButton("❌")
        btn_delete.setStyleSheet(self.button_style("#FF5A5A", "#FF8585"))
        self.setCellWidget(row_position, 5, btn_delete)

        # Bouton Options
        btn_opt = QPushButton("☰")
        btn_opt.setStyleSheet(self.button_style("#575656", "#adaaaa"))
        # Connecter le menu de configuration
        btn_opt.clicked.connect(lambda: self.show_config_menu(watcher_id, btn_opt))
        self.setCellWidget(row_position, 6, btn_opt)

        if save:
            # Save Watcher Config
            Tools().set_pattern(watcher_id, input_dir=input_dir, output_dir=output_dir)
        # Création du watcher
        #watcher = Watcher(input_dir, output_dir, id=watcher_id, auto_mode=auto)
        #self.watchers.append((watcher, auto_checkbox, status_label, btn_run, btn_delete, progress_statut))

        # Connecte le signal toggled de la case à cocher
        # Si auto on active la checkbox
        auto_checkbox.toggled.connect(lambda: self.update_auto_status(watcher, auto_checkbox, status_label))
        if auto:
            auto_checkbox.toggle()

        # Connexion des actions
        btn_run.clicked.connect(lambda: self.run_watcher(watcher=watcher))
        btn_delete.clicked.connect(lambda: self.delete_watcher(watcher.id))
        print(len(self.watcher_manager.watchers))

    def create_table_item(self, text, center=False):
        item = QTableWidgetItem(text)
        item.setForeground(QColor("#F0F0F0"))
        if center:
            item.setTextAlignment(Qt.AlignCenter)
        return item

    def run_watcher(self, watcher, debug=False):
        """Exécute manuellement le traitement d'un watcher."""
        row = self.get_row_by_watcher_id(watcher.id)
        print(f'Ligne trouvé dans runWatcher: {row}')
        progress_statut = self.cellWidget(row, 3)  # Correction ici
        self.thread = PDFProcessorThread(watcher=watcher, debug=debug)
        self.thread.finished_signal.connect(
            lambda value: self.on_processing_finished(value, progress_statut, style="color: #00FF00;"))
        self.thread.progress_signal.connect(lambda value: self.update_progress(value, progress_statut))
        self.thread.start()

    def update_progress(self, message, output,style=False):
        """Met à jour la barre de progression."""
        output.setText(message)
        if style:
            output.setStyleSheet(style)

    def on_processing_finished(self, message, output,style=False):
        """Met à jour la barre de progression."""
        output.setText(message)
        if style:
            output.setStyleSheet(style)

    def update_auto_status(self, watcher,checkbox, status_label):
        """Met à jour le statut automatique en fonction de la case à cocher."""
        if checkbox.isChecked():
            watcher.auto_mode = True
            watcher.start()
            status_label.setText("ON")
            status_label.setStyleSheet("color: #00FF00;")

        else:
            watcher.stop()
            watcher.auto_mode = False
            status_label.setText("OFF")
            status_label.setStyleSheet("color: #FF5A5A;")
        Tools().set_pattern(watcher.id, auto=watcher.auto_mode)

    def delete_watcher(self, watcher_id):
        """Supprime un watcher de la liste et du tableau."""
        row = self.get_row_by_watcher_id(watcher_id)
        if row is not None:
            print(f"✅ Suppression du watcher {watcher_id} à la ligne {row}")

            # Arrêter le watcher s'il est en cours d'exécution
            watcher = self.watcher_manager.get_watcher(watcher_id)
            if watcher:
                watcher.stop()

            # Supprimer la ligne du tableau
            self.removeRow(row)

            # Supprimer le watcher du WatcherManager
            self.watcher_manager.remove_watcher(watcher_id)

            # Supprimer la configuration du watcher
            tools = Tools()
            patterns = tools.load_patterns()
            if str(watcher_id) in patterns:
                del patterns[str(watcher_id)]
                tools.save_patterns(patterns)
                print(f"✅ Configuration du watcher {watcher_id} supprimée")
        else:
            print(f"❌ Impossible de trouver le watcher {watcher_id}")

    def get_row_by_watcher_id(self, watcher_id):
        """Trouve la ligne correspondant à un watcher_id."""
        for row in range(self.rowCount()):
            input_item = self.item(row, 0)
            if input_item and input_item.data(Qt.UserRole) == watcher_id:
                print(f"✅ Watcher {watcher_id} trouvé à la ligne {row}")
                return row

        print(f"❌ Ligne non trouvée pour le watcher ID: {watcher_id}")
        return None

    def button_style(self, bg_color, hover_color):
        """Style pour les boutons de la table"""
        return f"""
            QPushButton {{
                background-color: {bg_color};
                border: none;
                border-radius: 4px;
                padding: 5px;
                color: white;
                min-width: 60px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """
    def load_watchers_from_json(self):
        """Charge les watchers depuis un fichier JSON et les ajoute à l'interface."""
        try:
            data = Tools().load_patterns()

            for id, watcher in data.items():
                if id!="DEFAULT":
                    self.add_watcher(
                        input_dir=watcher.get("input_dir",False),
                        output_dir=watcher.get("output_dir",False),
                        id=id,
                        auto=watcher.get("auto",False),
                    )

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Erreur lors du chargement des watchers : {e}")

    def show_config_menu(self, watcher_id, button):
        """Affiche le menu de configuration pour un watcher."""
        menu = WatcherConfigMenu(watcher_id, self)
        # Positionner le menu sous le bouton
        pos = button.mapToGlobal(button.rect().bottomLeft())
        menu.exec_(pos)
