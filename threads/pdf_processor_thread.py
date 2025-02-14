from PyQt5.QtCore import QThread, pyqtSignal
from logic.core import PDFProcessor

class PDFProcessorThread(QThread):
    """Thread pour exécuter le traitement PDF sans bloquer l'interface."""

    # Signal pour informer la fin du traitement et pour la progression
    finished_signal = pyqtSignal(str)  # Signal pour indiquer la fin du traitement
    progress_signal = pyqtSignal(str)  # Signal pour mettre à jour l'état du traitement

    def __init__(self, watcher, debug):
        super().__init__()
        self.input_dir = watcher.input_dir
        self.output_dir = watcher.output_dir
        self.id = watcher.id
        self.debug = debug

    def run(self):
        """Exécution du traitement PDF en arrière-plan."""
        print(f'📄 Traitement en cours pour le watcher ID : {self.id}')
        self.progress_signal.emit("En cours")

        processor = PDFProcessor(self.input_dir, self.output_dir, self.id, self.debug)
        processor.process()

        self.finished_signal.emit("Traitement terminé!")  # Émission du signal une fois terminé
