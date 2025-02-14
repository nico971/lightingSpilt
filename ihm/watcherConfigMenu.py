from PyQt5.QtWidgets import QMenu, QAction, QWidget, QCheckBox
from PyQt5.QtWidgets import QWidgetAction
from .drawPattern import DrawPatternDialog
from utils.tools import Tools

class WatcherConfigMenu(QMenu):
    def __init__(self, watcher_id, parent=None):
        super().__init__(parent)
        self.watcher_id = watcher_id
        self.parent = parent
        self.tools = Tools()
        self.init_menu()

    def init_menu(self):
        # Action pour dessiner le pattern
        draw_pattern_action = QAction("✏️ Dessiner le pattern", self)
        draw_pattern_action.triggered.connect(lambda: DrawPatternDialog(pattern_id=self.watcher_id).exec_())
        self.addAction(draw_pattern_action)

        # Action pour modifier les chemins
        edit_paths_action = QAction("📁 Modifier les chemins", self)
        # edit_paths_action.triggered.connect(self.edit_paths)
        self.addAction(edit_paths_action)

        # Séparateur
        self.addSeparator()

        # Sous-menu "Après traitement"
        post_process_menu = QMenu("🔄 Après traitement", self)
        
        # Widget pour la checkbox
        checkbox_widget = QWidget()
        self.delete_source_checkbox = QCheckBox("Supprimer fichier source")
        self.delete_source_checkbox.setStyleSheet("color: white;")
        
        # Charger l'état sauvegardé
        patterns = self.tools.load_patterns()
        if str(self.watcher_id) in patterns:
            delete_source = patterns[str(self.watcher_id)].get('delete_source', False)
            self.delete_source_checkbox.setChecked(delete_source)
        
        # Connecter le changement d'état
        self.delete_source_checkbox.stateChanged.connect(self.on_delete_source_changed)
        
        # Créer une action widget pour la checkbox
        checkbox_action = QWidgetAction(self)
        checkbox_action.setDefaultWidget(self.delete_source_checkbox)
        
        # Ajouter la checkbox au sous-menu
        post_process_menu.addAction(checkbox_action)
        
        # Ajouter le sous-menu au menu principal
        self.addMenu(post_process_menu)

        # Séparateur
        self.addSeparator()

        # Action pour réinitialiser
        reset_action = QAction("🔄 Réinitialiser", self)
        # reset_action.triggered.connect(self.reset_watcher)
        self.addAction(reset_action)

    def on_delete_source_changed(self, state):
        """Gère le changement d'état de la checkbox de suppression"""
        delete_source = bool(state)
        # Sauvegarder la préférence
        patterns = self.tools.load_patterns()
        if str(self.watcher_id) in patterns:
            patterns[str(self.watcher_id)]['delete_source'] = delete_source
            self.tools.save_patterns(patterns)
            print(f"✅ Préférence de suppression mise à jour : {delete_source}") 