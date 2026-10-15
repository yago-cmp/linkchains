import time
import json
import sqlite3
import subprocess

def conexao_db():
    return sqlite3.connect('freechains_index.db', check_same_thread=False)

def worker_sync(nome_chain, peers): # roda em 2 plano
    conn = conexao_db()
    cursor = conn.cursor()
    while True:
        try:
            print("[Sync] Buscando novos blocos...")
            #para cada peer conectado da lista, faz um recv
            for peer in peers:
                subprocess.run(["freechains", "chain", nome_chain, "recv", peer], capture_output=True, check=True)

            #pega todos os hashes de postagens
            hashes = subprocess.run(["freechains", "chain", nome_chain, "heads"], capture_output=True, text=True, check=True)
            #separa eles numa lista                        
            hashes_lista = hashes.stdout.strip().split('\n')
            #verifica a existencia de cada um dos hashes no banco sqlite
            for hash_id in hashes_lista:
                if not hash_id: #seguranca para itens vazios
                    continue
                cursor.execute("SELECT 1 FROM Mensagens WHERE hash_id = ?", (hash_id,))
                existe_no_banco = cursor.fetchone()
                
                if not existe_no_banco:
                    # adiciona o novo post no banco sqlite
                    adicionar_post_sql(hash_id, conn, cursor)
        
            print("[Sync] SQLite atualizado!")

        except Exception as error:
            print(f"[Sync] Falha na sincronização: {error}")
        time.sleep(20) # sincroniza a cada 20 segundos

def enviar_post_rede(titulo, tags, link, nome_chain):
    #formatacao para json
    payload = {"titulo": titulo, "tags": tags, "link": link}
    payload_json = json.dumps(payload)
    try:
        subprocess.run(["freechains", "chain", nome_chain, "post", "inline", payload_json], check=True)
        print(f"Post enviado para o Freechains: {payload_json}")
        return True
    except subprocess.CalledProcessError:
        return False