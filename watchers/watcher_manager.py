from watchers.watcher import Watcher

class WatcherManager:
    _instance = None  # Stocke l'instance unique

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WatcherManager, cls).__new__(cls)
            cls._instance.watchers = []  # Initialise une seule fois la liste des watchers
        return cls._instance

    def add_watcher(self, input_dir, output_dir, watcher_id, auto):
        watcher = Watcher(input_dir, output_dir, id=watcher_id, auto_mode=auto)
        self.watchers.append(watcher)
        return watcher

    def remove_watcher(self, watcher_id):
        self.watchers = [w for w in self.watchers if w.id != watcher_id]

    def are_watchers_running(self):
        """Vérifie si des watchers sont en cours d'exécution."""
        return any(watcher.running for watcher in self.watchers)

    def get_watcher(self, watcher_id):
        """Récupère un watcher par son ID."""
        return next((w for w in self.watchers if w.id == watcher_id), None)

    def get_all_watchers(self):
        """Retourne tous les watchers."""
        return self.watchers
