from PyQt5.QtWidgets import QAction
from .drawPattern import DrawPatternDialog

def create_menu(window):
    menubar = window.menuBar()

    # Menu Fichier
    file_menu = menubar.addMenu("Fichier")
    quit_action = QAction("Quitter", window)
    quit_action.triggered.connect(window.quit_app)
    file_menu.addAction(quit_action)

    # Menu Outils
    tools_menu = menubar.addMenu("Outils")
    pattern_action = QAction("Dessiner un Pattern", window)
    pattern_action.triggered.connect(lambda: DrawPatternDialog().exec_())
    tools_menu.addAction(pattern_action)

    # Menu Aide
    help_menu = menubar.addMenu("Aide")
    about_action = QAction("À propos", window)
    help_menu.addAction(about_action)