from watchers.watcher import Watcher

class WatcherManager:
    def __init__(self):
        self.watchers = []

    def add_watcher(self, input_dir, output_dir, watcher_id, auto):
        watcher = Watcher(input_dir, output_dir, id=watcher_id, auto_mode=auto)
        self.watchers.append(watcher)
        return watcher

    def remove_watcher(self, watcher_id):
        self.watchers = [w for w in self.watchers if w.id != watcher_id]
