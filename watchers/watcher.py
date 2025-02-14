import os
import time
import threading
from logic.core import PDFProcessor

class Watcher:
    """Surveille un dossier et traite les PDF dès qu'ils apparaissent en mode auto."""

    def __init__(self, input_dir, output_dir,id,auto_mode=False):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.id = id
        self.auto_mode = auto_mode
        self.processor = PDFProcessor(input_dir, output_dir,pattern=id,debug=False)
        self.running = False
        self.thread = None

    def watch(self):
        """Démarre la surveillance en continu si le mode auto est activé."""
        self.running = True
        seen_files = set(os.listdir(self.input_dir))

        while self.running:
            time.sleep(2)
            current_files = set(os.listdir(self.input_dir))
            new_files = current_files - seen_files

            for file in new_files:
                if file.lower().endswith(".pdf"):
                    print(f"[Watcher] Nouveau fichier détecté : {file}")
                    self.processor.split_pdf(os.path.join(self.input_dir, file), self.output_dir)

            seen_files = current_files

    def start(self):
        """Lance la surveillance dans un thread séparé."""
        if self.auto_mode and not self.running:
            self.thread = threading.Thread(target=self.watch, daemon=True)
            self.thread.start()

    def stop(self):
        """Arrête la surveillance."""
        self.running = False
