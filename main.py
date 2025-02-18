import sys
from PyQt5.QtWidgets import QApplication
from ihm.main_window import PDFWatcherApp


def main():
    """Fonction principale pour démarrer l'application."""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Empêcher la fermeture complète sur fermeture de la fenêtre

    window = PDFWatcherApp()  # Crée l'instance de la fenêtre principale
    window.show()  # Affiche la fenêtre
    exit_code = app.exec_()  # Lance la boucle d'événements de l'application

    # Appeler QApplication.quit() si nécessaire pour fermer l'application proprement
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
