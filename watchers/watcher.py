import os
import time
import threading
from logic.core import PDFProcessor
from utils.tools import Tools

class Watcher:
    """Surveille un dossier et traite les PDF dès qu'ils apparaissent en mode auto."""

    def __init__(self, input_dir, output_dir,id,auto_mode=False):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.id = id
        self.auto_mode = auto_mode
        self.processor = PDFProcessor(input_dir, output_dir,pattern_id=id,debug=False)
        self.watching = False
        self.running = False
        self.thread = None

    def watch(self):
        """Démarre la surveillance en continu si le mode auto est activé."""
        self.watching = True
        seen_files = set(os.listdir(self.input_dir))

        while self.watching:
            time.sleep(2)
            current_files = set(os.listdir(self.input_dir))
            new_files = current_files - seen_files

            for file in new_files:
                if file.lower().endswith(".pdf"):
                    file_path = os.path.join(self.input_dir, file)
                    print(f"[Watcher] Nouveau fichier détecté : {file}")

                    # Attente que la copie soit complète et le fichier lisible
                    if Tools().wait_for_copy_complete(file_path):
                        self.running = True
                        print(f"[Watcher] Copie terminée, traitement du fichier : {file}")
                        try:
                            self.processor.split_pdf(file_path, self.output_dir)
                        except Exception as e:
                            print(f"[Watcher]  Erreur lors du traitement de {file} : {e}")
                        self.running = False
                    else:
                        print(f"[Watcher]  Le fichier {file} n'a pas pu être validé (copie incomplète ?)")

            seen_files = current_files

    def start(self):
        """Lance la surveillance dans un thread séparé."""
        if self.auto_mode and not self.watching:
            self.thread = threading.Thread(target=self.watch, daemon=True)
            self.thread.start()

    def stop(self):
        """Arrête la surveillance."""
        self.watching = False
