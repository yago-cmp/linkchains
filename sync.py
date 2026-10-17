import time
import json
import sqlite3
import subprocess
import os

def chain_existe(nome_chain):
    try:
        result = subprocess.run(["freechains", "chains", "dir"], capture_output=True, text=True, check=True)
        return nome_chain in result.stdout.split()
    except subprocess.CalledProcessError:
        return False
    
def iniciar_chain(nome_chain, peer=None, chave="./tmp/chaves/user.pub"):
    try:
        with open(chave, 'r') as arquivo:
            chave_texto = arquivo.read().strip()
        resultado = subprocess.run(["freechains", "chains", "dir"], capture_output=True, text=True, check=True)
        chains = resultado.stdout.split()

        if nome_chain in chains: # se a chain ja existe, retorna
            print(f"[Chain] {nome_chain} já existe localmente.")
            return True         

        if peer: # se recebe um peer, clona dele a cadeia
            print(f"[Chain] Clonando de: {peer}")
            subprocess.run(["freechains", "chains", "add", nome_chain, "clone", peer],capture_output=True, check=True)
        else: # se nao recebe um peer, cria a cadeia do zero
            print("[Setup] Criando nova cadeia vazia do zero.")
            subprocess.run(["freechains", "chains", "add", nome_chain, "init", f"--pioneer={chave_texto}"],capture_output=True, check=True)    
        return True

    except subprocess.CalledProcessError as e: # caso algum subprocess encontre um erro
            print(f"[Erro] Falha ao configurar a cadeia: {e.stderr}")
            return False

def iniciar_db(conn, cursor): # cria as tabelas para iniciar o teste
    cursor.execute("CREATE TABLE IF NOT EXISTS Mensagens (hash_id TEXT PRIMARY KEY, titulo TEXT, link TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Tags (hash_id TEXT, tag_name TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Peers (endereco TEXT UNIQUE)")
    conn.commit()

def deletar_db(conn, cursor): # deleta as tabelas para reiniciar o teste
    cursor.execute("DROP TABLE Mensagens")
    cursor.execute("DROP TABLE Tags")
    cursor.execute("DROP TABLE Peers")
    conn.commit()

def recv_peers(nome_chain, cursor): # faz o recv de todos os peers conhecidos
    print("[SYNC] Buscando novos posts!")
    cursor.execute("SELECT endereco FROM Peers")
    lista = cursor.fetchall()
    #para cada peer conhecido da lista, faz um recv
    for peer in lista:
        subprocess.run(["freechains", "chain", nome_chain, "recv", peer], capture_output=True, check=True)

def limpar_revogados(nome_chain, conn, cursor):
    cursor.execute("SELECT hash_id FROM Mensagens")
    hashes_no_banco = [linha[0] for linha in cursor.fetchall()]
    
    for hash_db in hashes_no_banco:
        try:
            subprocess.run(["freechains", "chain", nome_chain, "get", "payload", hash_db], capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            erro_msg = e.stderr.lower()
            if "revoked" in erro_msg or "not found" in erro_msg: #se for revogado
                cursor.execute("DELETE FROM Mensagens WHERE hash_id = ?", (hash_db,))
                cursor.execute("DELETE FROM Tags WHERE hash_id = ?", (hash_db,))
                conn.commit()
                print(f"[LIMPEZA] Post revogado deletado do SQLite!")

def worker_sync(nome_chain, conn, cursor, continuo): # roda em 2 plano, constantemente
    while continuo:
        try:
            recv_peers(nome_chain, cursor)

            #pega todos os hashes de postagens
            hashes = subprocess.run(["freechains", "chain", nome_chain, "list", "order"], capture_output=True, text=True, check=True)
            hashes_lista = hashes.stdout.strip().split('\n')#separa eles numa lista   

            for hash_id in hashes_lista:#verifica a existencia de cada um dos hashes no banco sqlite
                if not hash_id: #seguranca para itens vazios
                    continue
                cursor.execute("SELECT 1 FROM Mensagens WHERE hash_id = ?", (hash_id,))
                existe_no_banco = cursor.fetchone()
                
                if not existe_no_banco:
                    # adiciona o novo post no banco sqlite
                    salvar_post(nome_chain, hash_id, conn, cursor)

            limpar_revogados(nome_chain, conn, cursor) # analisa o banco e remove os revogados
        
            print("[SYNC] SQLite atualizado!")

        except Exception as error:
            print(f"[SYNC Falha na sincronização: {error}")
        time.sleep(8) # sincroniza a cada 8 segundos

def salvar_post(nome_chain, hash_id, conn, cursor):
    try: 
        dados_post = subprocess.run(["freechains", "chain", nome_chain, "get", "payload", hash_id], capture_output=True, text=True, check=True)
        try:
            payload = json.loads(dados_post.stdout)
            cursor.execute("INSERT INTO Mensagens (hash_id, titulo, link) VALUES (?, ?, ?)", (hash_id, payload['titulo'], payload['link']))
            for tag in payload['tags']:
                cursor.execute("INSERT INTO Tags (hash_id, tag_name) VALUES (?, ?)", (hash_id, tag))
            conn.commit()
            return True
        except json.JSONDecodeError:
            cursor.execute("INSERT INTO Mensagens (hash_id, titulo, link) VALUES (?, ?, ?)", (hash_id, "BLOCO_DE_ACAO", ""))
            conn.commit()
            return True
    except subprocess.CalledProcessError as e: # caso algum subprocess encontre um erro
        print(f"[SALVAR] Post Revogado ou Erro: {e.stderr}")
        cursor.execute("INSERT INTO Mensagens (hash_id, titulo, link) VALUES (?, ?, ?)", (hash_id, "REVOGADO", ""))
        conn.commit()
        return False

def enviar_post(titulo, tags, link, nome_chain, chave="./tmp/chaves/user"):
    caminho_abs = os.path.abspath(chave) 
    #formatacao para json
    payload = {"titulo": titulo, "tags": tags, "link": link}
    payload_json = json.dumps(payload)
    try:
        if reps(nome_chain) == 0: # se nao tem reps, faz um beg
            subprocess.run(["freechains", "chain", nome_chain, "post", "inline", payload_json, "--beg", f"--sign={caminho_abs}"], check=True)
            print(f"Post enviado para o Freechains: {payload_json}")
        else:
            subprocess.run(["freechains", "chain", nome_chain, "post", "inline", payload_json, f"--sign={caminho_abs}"], check=True)
            print(f"Post enviado para o Freechains: {payload_json}")
        return True
    except subprocess.CalledProcessError:
        return False

def gorjeta(hash_id, qtd, nome_chain, chave="./tmp/chaves/user"): # like
    try:
        caminho_abs = os.path.abspath(chave)  
        subprocess.run(["freechains", "chain", nome_chain, "like", str(qtd), "action", hash_id, f"--sign={caminho_abs}"], check=True)
        print(f"Gorjeta enviada!")
        return True
    except subprocess.CalledProcessError:
        return False

def denuncia(hash_id, qtd, nome_chain, chave="./tmp/chaves/user"): # revoke
    try:
        caminho_abs = os.path.abspath(chave)  
        subprocess.run(["freechains", "chain", nome_chain, "revoke", str(qtd), hash_id, f"--sign={caminho_abs}"], check=True)
        print(f"Denuncia enviada!")
        return True
    except subprocess.CalledProcessError:
        return False

def sinalizacao(hash_id, qtd, nome_chain, chave="./tmp/chaves/user"): # dislike
    try:
        caminho_abs = os.path.abspath(chave)
        subprocess.run(["freechains", "chain", nome_chain, "dislike", str(qtd), "action", hash_id, f"--sign={caminho_abs}"], check=True)
        print(f"Dislike enviado!")
        return True
    except subprocess.CalledProcessError:
        return False

def busca(lista_tags, cursor):
    if not lista_tags:
            return []
    placeholder = ', '.join(['?'] * len(lista_tags))
    qtd_tags = len(lista_tags)

    query = f'''SELECT m.hash_id, m.titulo, m.link 
            FROM Mensagens m
            JOIN Tags t ON m.hash_id = t.hash_id
            WHERE LOWER(t.tag_name) IN ({placeholder})
            GROUP BY m.hash_id
            HAVING COUNT(DISTINCT LOWER(t.tag_name)) = ?
        '''
    try:
        cursor.execute(query, lista_tags + [qtd_tags]) # passa os parametros como lista
        resultados = cursor.fetchall() # lista de payloads com todos
        return resultados
    except Exception as error:
        print(f"[BUSCA] Erro buscando: {error}")
        return []

    
def remove_tudo(nome_chain, conn, cursor):
    print("Removendo tudo!")
    try:
        deletar_db(conn, cursor) # dropa as tabelas
        print("[RESET] Tabelas deletadas!")
    except Exception as e:
        print(f"[RESET] Erro ao deletar tabelas: {e}")

    try:
        subprocess.run(["freechains", "chains", "rem", nome_chain], capture_output=True, check=True)
        print(f"[RESET] Chain removida!")
    except subprocess.CalledProcessError as e:
        print(f"[RESET] Erro ao remover a chain: {e.stderr}")

    try:
        subprocess.run(["rm", "-rf", "./tmp/chaves"], capture_output=True, text=True, check=True)
        print("[RESET] Chaves removidas!")
    except subprocess.CalledProcessError as e:
            print(f"[RESET] Erro ao remover as chaves: {e.stderr}")
        
    return True


def add_peer_db(peer, conn, cursor):
    cursor.execute("INSERT INTO Peers (endereco) VALUES (?)", (peer,))
    conn.commit()
    print(f"[SQL] Peer {peer} adicionado ao DB!)")
    return True

def reps(nome_chain, chave="./tmp/chaves/user.pub"):
    try:
        caminho_abs = os.path.abspath(chave)

        resultado = subprocess.run(["freechains", "chain", nome_chain, "reps", "author", caminho_abs], capture_output=True, text=True, check=True)
        return resultado.stdout.strip()
        
    except FileNotFoundError:
        return "Chave não encontrada"