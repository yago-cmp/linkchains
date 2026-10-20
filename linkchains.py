from gui import AppGUI, Setup
from sync import worker_sync, iniciar_db, chain_existe
import threading
import subprocess
import sqlite3
import os

CHAIN_NAME = "#torrents"

conn = sqlite3.connect('freechains_index.db', check_same_thread=False)
cursor = conn.cursor()

iniciar_db(conn, cursor) # cria as tabelas do SQLite, caso nao existam

if __name__ == "__main__":
    if os.path.isfile("./tmp/chaves/user") == False: # se as chaves do usuario nao existem
        os.makedirs("./tmp/chaves", exist_ok=True) # cria a pasta
        subprocess.run(["ssh-keygen", "-t", "ed25519", "-N", "", "-C", "", "-f","./tmp/chaves/user"]) #cria as chaves do usuario

    if not chain_existe(CHAIN_NAME):
            setup_app = Setup(CHAIN_NAME, conn, cursor) # cria e inicia a GUI de setup inicial
            setup_app.mainloop() # programa pausa, janela inicial de setup
            
            if not chain_existe(CHAIN_NAME): # se apos o setup, nao houver chain
                print("Programa fechado!")
                exit() # fecha o programa

    thread_sync = threading.Thread(target=worker_sync, args=(CHAIN_NAME, conn, cursor, True), daemon=True)
    thread_sync.start() # cria e inicia a sincronizacao em outra thread

    app = AppGUI(CHAIN_NAME, conn, cursor) # cria e inicia a GUI na thread principal
    app.mainloop()
