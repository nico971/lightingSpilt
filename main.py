import sys
from PyQt5.QtWidgets import QApplication
from ihm.main_window import PDFWatcherApp

def main():
    """Fonction principale pour démarrer l'application."""
    app = QApplication(sys.argv)
    window = PDFWatcherApp()  # Crée l'instance de la fenêtre principale
    window.show()  # Affiche la fenêtre
    sys.exit(app.exec_())  # Lance la boucle d'événements de l'application

if __name__ == "__main__":
    main()
