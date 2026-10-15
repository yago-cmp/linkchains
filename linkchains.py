from gui import AppGUI 
from sync import worker_sync
import threading
import subprocess

# Configurações globais
CHAIN_NAME = "#torrents"
FREECHAINS_CMD = "freechains"
PEER_CONHECIDO = "localhost:8333"

if __name__ == "__main__":

    thread_sync = threading.Thread(target=worker_sync, daemon=True)
    thread_sync.start()
    
    app = AppGUI()
    app.mainloop()