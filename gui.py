import customtkinter as ctk
import sys
import os
from PIL import Image
from sync import enviar_post, sinalizacao, gorjeta, denuncia, iniciar_chain, busca, remove_tudo, reps, recv_peers, add_peer_db
import subprocess
import json 

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class Setup(ctk.CTk):
    def __init__(self, nome_chain):
        super().__init__()
        self.nome_chain = nome_chain
        
        self.title("LinkChains Setup")
        self.geometry("450x250")
        try:
            self.iconbitmap("freechains_logo.ico")
        except Exception:
            pass
        # texto da pagina
        self.lbl_titulo = ctk.CTkLabel(self, text=f"Seja bem-vindo ao LinkChains!", font=ctk.CTkFont(weight="bold", size=20))
        self.lbl_titulo.pack(pady=(30, 20))

        self.lbl_info = ctk.CTkLabel(self, text=f"Como iniciar a #torrents?", font=ctk.CTkFont(weight="bold", size=16))
        self.lbl_info.pack(pady=(10, 10))
        
        # botao de criar
        self.btn_criar = ctk.CTkButton(self, text="Criar Cadeia!", command=self.criar_zero, fg_color="MediumPurple2", hover_color="MediumPurple4")
        self.btn_criar.pack(pady=10)
        
        # botao de clonar
        self.frame_clone = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_clone.pack(pady=10)
        
        self.entry_peer = ctk.CTkEntry(self.frame_clone, placeholder_text="Ex: 192.168.1.5:8330", width=220)
        self.entry_peer.pack(side="left", padx=(0, 10))
        
        self.btn_clone = ctk.CTkButton(self.frame_clone, text="Clonar!", command=self.clonar_peer, fg_color="MediumPurple2", hover_color="MediumPurple4", width=80)
        self.btn_clone.pack(side="left")

    def criar_zero(self):
        if iniciar_chain(self.nome_chain, self.conn, self.cursor): # inicia a chain
            self.destroy() # se iniciou, fecha janela

    def clonar_peer(self):
        peer = self.entry_peer.get().strip()
        if peer:
            if iniciar_chain(self.nome_chain, self.conn, self.cursor, peer): 
                self.destroy()

class AppGUI(ctk.CTk):
    def __init__(self, nome_chain, conn, cursor):
        super().__init__()

        self.nome_chain = nome_chain # define como self para diminuir parametros
        self.cursor = cursor
        self.conn = conn

        self.title("LinkChains")
        self.geometry("1200x600")
        try:
            self.iconbitmap("freechains_logo.ico")
        except Exception:
            pass

        # grid colunas
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)        
        self.grid_rowconfigure(0, weight=1)
        
        # --- COLUNA DA ESQUERDA ---
        self.frame_lateral = ctk.CTkFrame(self, width=400, corner_radius=0)
        self.frame_lateral.grid(row=0, column=0, sticky="nsew")
        
        # frame para a logo e titulo
        self.frame_logo = ctk.CTkFrame(self.frame_lateral, fg_color="transparent")
        self.frame_logo.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # logo do freechains
        caminho_imagem = os.path.join(os.path.dirname(os.path.abspath(__file__)), "freechains_logo.png")
        try:
            logo_img = ctk.CTkImage(light_image=Image.open(caminho_imagem),dark_image=Image.open(caminho_imagem), size=(30, 30)) 
            self.lbl_icone = ctk.CTkLabel(self.frame_logo, image=logo_img, text="")
            self.lbl_icone.pack(side="left", padx=(0, 10))
        except Exception as e:
            print(f"Não foi possível carregar a logo. Erro: {e}")

        # linkchains em cima
        self.titulo = ctk.CTkLabel(self.frame_logo, text="LinkChains", font=ctk.CTkFont(size=20, weight="bold"))

        self.titulo.pack(side="left")

        # "Novo Post"
        self.post_novo = ctk.CTkLabel(self.frame_lateral, text="Novo Post", font=ctk.CTkFont(size=16, weight="bold"))
        self.post_novo.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w") # sticky="w" para alinhar à esquerda
        
        # entradas do post
        self.entry_titulo = ctk.CTkEntry(self.frame_lateral, placeholder_text="Título")
        self.entry_titulo.grid(row=2, column=0, padx=20, pady=10, sticky="ew") # Mudou para row=2
        
        self.entry_tags = ctk.CTkEntry(self.frame_lateral, placeholder_text="Tags (X, Y, Z)")
        self.entry_tags.grid(row=3, column=0, padx=20, pady=10, sticky="ew") # Mudou para row=3
        
        self.entry_link = ctk.CTkEntry(self.frame_lateral, placeholder_text="Link")
        self.entry_link.grid(row=4, column=0, padx=20, pady=10, sticky="ew") # Mudou para row=4

        #botao post
        self.btn_enviar = ctk.CTkButton(self.frame_lateral, text="Postar", fg_color="MediumPurple2", hover_color="MediumPurple4", command=self.evento_postar)
        self.btn_enviar.grid(row=5, column=0, padx=20, pady=20) # Mudou para row=5

        # reset
        self.frame_lateral.grid_rowconfigure(6, weight=1) # Empurra o reset para baixo
        self.btn_reset = ctk.CTkButton(self.frame_lateral, text="Reset", fg_color="MediumPurple2", hover_color="red", command=self.evento_resetar)
        self.btn_reset.grid(row=7, column=0, padx=20, pady=20, sticky="s")
        
        # --- COLUNA DO MEIO ---
        self.frame_principal = ctk.CTkFrame(self)
        self.frame_principal.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.frame_principal.grid_rowconfigure(1, weight=1)
        self.frame_principal.grid_columnconfigure(0, weight=1)
        
        # barra de busca
        self.frame_busca = ctk.CTkFrame(self.frame_principal, fg_color="transparent")
        self.frame_busca.grid(row=0, column=0, sticky="ew")
        self.frame_busca.grid_columnconfigure(0, weight=1)
        
        self.entry_busca = ctk.CTkEntry(self.frame_busca, placeholder_text="Buscar por Tags e Título (Título, X, Y, Z")
        self.entry_busca.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="ew")
        
        self.btn_buscar = ctk.CTkButton(self.frame_busca, text="Buscar", fg_color="MediumPurple2", hover_color="MediumPurple4", command=self.evento_buscar)
        self.btn_buscar.grid(row=0, column=1, pady=10)
        
        # Feed de Conteúdo (Scrollable)
        self.scroll_feed = ctk.CTkScrollableFrame(self.frame_principal, label_text="Conteúdos Encontrados")
        self.scroll_feed.grid(row=1, column=0, sticky="nsew")


# --- COLUNA DA DIREITA ---
        self.frame_begs = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.frame_begs.grid(row=0, column=2, sticky="nsew")
        self.frame_begs.grid_columnconfigure(0, weight=1)
        self.frame_begs.grid_rowconfigure(2, weight=1) 
        self.frame_begs.grid_rowconfigure(6, weight=1) 

        # --- REPS ---
        self.lbl_reps = ctk.CTkLabel(self.frame_begs, text=f"Reps: {reps(self.nome_chain)}", font=ctk.CTkFont(size=16, weight="bold"), text_color="MediumPurple2")
        self.lbl_reps.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        # --- BEGS ---
        self.titulo_begs = ctk.CTkLabel(self.frame_begs, text="Begs Pendentes", font=ctk.CTkFont(size=16, weight="bold"))
        self.titulo_begs.grid(row=1, column=0, padx=10, pady=(10, 5))

        self.scroll_begs = ctk.CTkScrollableFrame(self.frame_begs, fg_color="transparent")
        self.scroll_begs.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

        self.btn_atualizar_begs = ctk.CTkButton(self.frame_begs, text="Atualizar Begs", fg_color="MediumPurple2", hover_color="MediumPurple4", command=self.carregar_begs)
        self.btn_atualizar_begs.grid(row=3, column=0, padx=10, pady=5)

        # --- PEERS ---
        # linha
        self.separador = ctk.CTkFrame(self.frame_begs, height=2, fg_color="gray")
        self.separador.grid(row=4, column=0, sticky="ew", padx=20, pady=10)

        self.titulo_peers = ctk.CTkLabel(self.frame_begs, text="Peers (Rede)", font=ctk.CTkFont(size=16, weight="bold"))
        self.titulo_peers.grid(row=5, column=0, padx=10, pady=(5, 5))

        self.scroll_peers = ctk.CTkScrollableFrame(self.frame_begs, fg_color="transparent")
        self.scroll_peers.grid(row=6, column=0, sticky="nsew", padx=10, pady=5)

        # frame para add peers
        self.frame_add_peer = ctk.CTkFrame(self.frame_begs, fg_color="transparent")
        self.frame_add_peer.grid(row=7, column=0, sticky="ew", padx=10, pady=(5, 20))
        self.frame_add_peer.grid_columnconfigure(0, weight=1)

        self.entry_novo_peer = ctk.CTkEntry(self.frame_add_peer, placeholder_text="Ex: 192.168.0.5:8330", width=150)
        self.entry_novo_peer.grid(row=0, column=0, padx=(0, 5))

        self.btn_add_peer = ctk.CTkButton(self.frame_add_peer, text="+", width=40, fg_color="MediumPurple2", hover_color="MediumPurple4", command=self.evento_adicionar_peer)
        self.btn_add_peer.grid(row=0, column=1)

        self.carregar_begs() # mostra todos os begs
        self.carregar_peers() # mostra todos os peers
  
    # eventos!! ---------------------------------------------------------------------------

    def carregar_begs(self):
        # retira os begs atuais
        for widget in self.scroll_begs.winfo_children():
            widget.destroy()           
        try:
            # lista os begs todos
            result = subprocess.run(["freechains", "chain", self.nome_chain, "list", "begs"], capture_output=True, text=True, check=True)
            hashes_begs = result.stdout.strip().split('\n')
            
            tem_begs = False
            for h in hashes_begs:
                if h:
                    tem_begs = True
                    # pega o payload de cada beg
                    res_payload = subprocess.run(["freechains", "chain", self.nome_chain, "get", "payload", h], capture_output=True, text=True, check=True)
                    payload = json.loads(res_payload.stdout)
                    titulo = payload.get('titulo', 'Sem título')
                    tags = payload.get('tags', [])
                    link = payload.get('link', '')

                    # exibe na tela cada um deles
                    self.adicionar_item_beg(h, titulo, tags, link)
                    
            if not tem_begs:
                ctk.CTkLabel(self.scroll_begs, text="Nenhum beg.").pack(pady=20)
                
        except Exception as e:
            ctk.CTkLabel(self.scroll_begs, text="Erro ao carregar begs.").pack(pady=20)
            print(f"Erro begs: {e}")

    def adicionar_item_beg(self, hash_id, titulo, tags, link):
        frame_beg = ctk.CTkFrame(self.scroll_begs, fg_color="#2b2b2b")
        frame_beg.pack(fill="x", padx=5, pady=5)

        # exibe o titulo do beg
        lbl_titulo = ctk.CTkLabel(frame_beg, text=titulo, font=ctk.CTkFont(size=16, weight="bold"))
        lbl_titulo.pack(anchor="w", padx=10, pady=(10, 0))

        # exibe as tags do beg
        lbl_tags = ctk.CTkLabel(frame_beg, text=f"Tags: {', '.join(tags)}", text_color="gray", font=ctk.CTkFont(size=12))
        lbl_tags.pack(anchor="w", padx=10, pady=(2, 5))

        # exibe o link do beg, selecionavel
        lbl_link = ctk.CTkEntry(frame_beg, width=200) 
        lbl_link.insert(0, link) 
        lbl_link.configure(state="readonly") 
        lbl_link.pack(anchor="w", padx=10, pady=(0, 10))

        # exibe o hash do beg
        hash_curto = hash_id[:15] + "..."
        lbl_hash = ctk.CTkLabel(frame_beg, text=f"Hash: {hash_curto}", font=ctk.CTkFont(size=10), text_color="darkgray")
        lbl_hash.pack(anchor="w", padx=10, pady=(0, 5))

        # aprovar beg
        btn_aprovar = ctk.CTkButton(frame_beg, text="Aprovar (500)", width=150, height=25, fg_color="green", hover_color="darkgreen", command=lambda: self.aprovar_beg(hash_id))
        btn_aprovar.pack(pady=(0, 10))

    def aprovar_beg(self, hash_id):
        recv_peers(self.nome_chain, self.cursor)

        sucesso = gorjeta(hash_id, "500", self.nome_chain)
        if sucesso:
            self.lbl_reps.configure(text=f"Reps atuais: {reps(self.nome_chain)}")
            self.carregar_begs()

    def evento_resetar(self):
        print("RESET EM ANDAMENTO")
        
        remove_tudo(self.nome_chain, self.conn, self.cursor) # remove a chain, as chaves e o .db

        self.destroy()
        sys.exit()

    def acao_gorjeta(self, hash_id, qtd):
        recv_peers(self.nome_chain, self.cursor)
        sucesso = gorjeta(hash_id, qtd, self.nome_chain)
        if sucesso:
            # atualiza os reps
            self.lbl_reps.configure(text=f"Reps: {reps(self.nome_chain)}")

    def acao_sinalizar(self, hash_id, qtd):
        recv_peers(self.nome_chain, self.cursor)
        sucesso = sinalizacao(hash_id, qtd, self.nome_chain)
        if sucesso:
            # atualiza reps
            self.lbl_reps.configure(text=f"Reps: {reps(self.nome_chain)}")

    def acao_denunciar(self, hash_id, qtd):
        recv_peers(self.nome_chain, self.cursor)
        sucesso = denuncia(hash_id, qtd, self.nome_chain)
        if sucesso:
            # atualiza os reps
            self.lbl_reps.configure(text=f"Reps: {reps(self.nome_chain)}")

    def evento_postar(self):
        titulo = self.entry_titulo.get()
        tags_raw = self.entry_tags.get()
        link = self.entry_link.get()
        
        if not titulo or not link:
            print("Preencha título e link!")
            return
            
        tags_lista = [t.strip().lower() for t in tags_raw.split(',') if t.strip()]
        tags_finais = [titulo.lower()] + tags_lista # titulo como tag para facilitar busca

        recv_peers(self.nome_chain, self.cursor) #recebe antes de enviar para evitar conflitos
        
        sucesso = enviar_post(titulo, tags_finais, link, self.nome_chain)
        if sucesso:
            self.entry_titulo.delete(0, 'end')
            self.entry_tags.delete(0, 'end')
            self.entry_link.delete(0, 'end')
            self.lbl_reps.configure(text=f"Reps: {reps(self.nome_chain)}")
            self.carregar_begs()

    def evento_buscar(self):
        termo = self.entry_busca.get()
        tags_pesquisa = [t.strip().lower() for t in termo.split(',') if t.strip()]
        
        for widget in self.scroll_feed.winfo_children():
            widget.destroy()
            
        resultados = busca(tags_pesquisa, self.cursor)
        
        if not resultados:
            ctk.CTkLabel(self.scroll_feed, text="Nenhum post encontrado!").pack(pady=20)
            return

        for item in resultados:
            hash_do_post = item[0]
            titulo = item[1]
            link = item[2]
            self.adicionar_item_feed(hash_do_post, titulo, tags_pesquisa, link)
        
    def adicionar_item_feed(self, hash_id, titulo, tags, link):
        frame_item = ctk.CTkFrame(self.scroll_feed)
        frame_item.pack(fill="x", padx=10, pady=5)
        
        # exibicao dos titulos
        lbl_titulo = ctk.CTkLabel(frame_item, text=titulo, font=ctk.CTkFont(size=20, weight="bold"))
        lbl_titulo.pack(anchor="w", padx=10, pady=(10, 0))

        #exibicao das tags
        lbl_tags = ctk.CTkLabel(frame_item, text=f"Tags: {', '.join(tags)}", text_color="gray", font=ctk.CTkFont(size=12))
        lbl_tags.pack(anchor="w", padx=10, pady=(2, 10))

        # exibicao do link
        lbl_link = ctk.CTkEntry(frame_item, width=400)  # entry para poder copiar conteudo
        lbl_link.insert(0, link) # mostra o link
        lbl_link.configure(state="readonly") # bloqueia alteracao
        lbl_link.pack(anchor="w", padx=10, pady=(0, 10))
        
        # frame para botoes
        frame_reps = ctk.CTkFrame(frame_item, fg_color="transparent")
        frame_reps.pack(fill="x", padx=10, pady=(0, 10))
        
        # qtd
        entry_qtd = ctk.CTkEntry(frame_reps, width=60, placeholder_text="Qtd")
        entry_qtd.pack(side="left", padx=(0, 10))      

        #gorjeta
        btn_tip = ctk.CTkButton(frame_reps, text="Gorjeta", width=120, fg_color="green", hover_color="darkgreen", command=lambda: self.acao_gorjeta(hash_id, entry_qtd.get()))
        btn_tip.pack(side="left", padx=(0, 10))

        #sinalizacao
        btn_sinalizar = ctk.CTkButton(frame_reps, text="Sinalizar", width=80, fg_color="#d48806", hover_color="#ad6e02", command=lambda: self.acao_sinalizar(hash_id, entry_qtd.get()))
        btn_sinalizar.pack(side="left", padx=(0, 10))

        #denuncia
        btn_denunciar = ctk.CTkButton(frame_reps, text="Denunciar", width=80, fg_color="red", hover_color="darkred", command=lambda: self.acao_denunciar(hash_id, entry_qtd.get()))
        btn_denunciar.pack(side="left")

    def carregar_peers(self):
        for widget in self.scroll_peers.winfo_children():
            widget.destroy()    #remove a lista atual
        try:
            self.cursor.execute("SELECT endereco FROM Peers") # pega todos os peers
            lista_peers = self.cursor.fetchall()
            if not lista_peers:
                ctk.CTkLabel(self.scroll_peers, text="Nenhum peer cadastrado.", text_color="gray").pack(pady=20)
                return
            for peer in lista_peers:
                endereco = peer[0] # fetchall retorna uma lista de tuplas, pega apenas o conteudo
                self.adicionar_item_peer(endereco)
                
        except Exception as e:
            ctk.CTkLabel(self.scroll_peers, text="Erro ao carregar peers.", text_color="red").pack(pady=20)
            print(f"[GUI] Erro ao listar peers: {e}")

    def adicionar_item_peer(self, endereco):
            frame_peer = ctk.CTkFrame(self.scroll_peers, fg_color="#2b2b2b")
            frame_peer.pack(fill="x", padx=5, pady=2)
            
            lbl_endereco = ctk.CTkLabel(frame_peer, text=endereco, font=ctk.CTkFont(size=12))
            lbl_endereco.pack(side="left", padx=10, pady=5)


    def evento_adicionar_peer(self):
            novo_peer = self.entry_novo_peer.get().strip()
            if not novo_peer:
                return          
            try:
                add_peer_db(novo_peer, self.conn, self.cursor)
                self.entry_novo_peer.delete(0, 'end')
                self.carregar_peers()   
            except Exception as e:
                print(f"[GUI] Falha ao adicionar peer (já existe ou erro SQL): {e}")
                self.entry_novo_peer.delete(0, 'end')
                self.entry_novo_peer.insert(0, "Erro/Duplicado")