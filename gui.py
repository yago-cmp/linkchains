import customtkinter as ctk
import sys
import os
from PIL import Image
from sync import enviar_post, sinalizacao, gorjeta, denuncia, iniciar_chain, busca, remove_tudo, reps, recv_peers

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
        if iniciar_chain(self.nome_chain, self.conn, self.cursor): # Chama função do sync.py
            self.destroy() # Se deu certo, fecha essa janela para a principal abrir

    def clonar_peer(self):
        peer = self.entry_peer.get().strip()
        if peer:
            if iniciar_chain(self.nome_chain, self.conn, self.cursor, peer): # Clona do IP digitado
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

        # Grid layout da janela principal
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)        
        self.grid_rowconfigure(0, weight=1)
        
        # --- MENU LATERAL (Envio de Conteúdo) ---
        self.frame_lateral = ctk.CTkFrame(self, width=400, corner_radius=0)
        self.frame_lateral.grid(row=0, column=0, sticky="nsew")
        
        # 1. Cria um Frame pequeno e invisível para alinhar o Logo e o Título lado a lado
        self.frame_logo = ctk.CTkFrame(self.frame_lateral, fg_color="transparent")
        self.frame_logo.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # 2. Carrega a imagem .png (certifique-se de que freechains_logo.png está na mesma pasta)
        caminho_imagem = os.path.join(os.path.dirname(os.path.abspath(__file__)), "freechains_logo.png")
        try:
            logo_img = ctk.CTkImage(light_image=Image.open(caminho_imagem),
                                    dark_image=Image.open(caminho_imagem),
                                    size=(30, 30)) # Ajuste o tamanho (largura, altura) se necessário
            self.lbl_icone = ctk.CTkLabel(self.frame_logo, image=logo_img, text="")
            self.lbl_icone.pack(side="left", padx=(0, 10))
        except Exception as e:
            print(f"Aviso: Não foi possível carregar a imagem freechains_logo.png. Erro: {e}")

        # 3. Adiciona o título "LinkChains" ao lado da imagem
        self.titulo = ctk.CTkLabel(self.frame_logo, text="LinkChains", font=ctk.CTkFont(size=20, weight="bold"))

        self.titulo.pack(side="left")

        # 4. Adiciona o subtítulo "Novo Post" abaixo do frame do logo
        self.post_novo = ctk.CTkLabel(self.frame_lateral, text="Novo Post", font=ctk.CTkFont(size=16, weight="bold"))
        self.post_novo.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w") # sticky="w" para alinhar à esquerda
        
        # 5. Entradas de texto (ajuste as linhas do grid porque adicionámos o post_novo)
        self.entry_titulo = ctk.CTkEntry(self.frame_lateral, placeholder_text="Título")
        self.entry_titulo.grid(row=2, column=0, padx=20, pady=10, sticky="ew") # Mudou para row=2
        
        self.entry_tags = ctk.CTkEntry(self.frame_lateral, placeholder_text="Tags (X, Y, Z)")
        self.entry_tags.grid(row=3, column=0, padx=20, pady=10, sticky="ew") # Mudou para row=3
        
        self.entry_link = ctk.CTkEntry(self.frame_lateral, placeholder_text="Link")
        self.entry_link.grid(row=4, column=0, padx=20, pady=10, sticky="ew") # Mudou para row=4
        
        self.btn_enviar = ctk.CTkButton(self.frame_lateral, text="Postar", fg_color="MediumPurple2", hover_color="MediumPurple4", command=self.evento_postar)
        self.btn_enviar.grid(row=5, column=0, padx=20, pady=20) # Mudou para row=5

        # --- BOTAO DE RESET ---
        self.frame_lateral.grid_rowconfigure(6, weight=1) # Empurra o reset para baixo
        self.btn_reset = ctk.CTkButton(self.frame_lateral, text="Reset", fg_color="MediumPurple2", hover_color="red", command=self.evento_resetar)
        self.btn_reset.grid(row=7, column=0, padx=20, pady=20, sticky="s")
        
        # --- ÁREA PRINCIPAL (Busca e Feed) ---
        self.frame_principal = ctk.CTkFrame(self)
        self.frame_principal.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.frame_principal.grid_rowconfigure(1, weight=1)
        self.frame_principal.grid_columnconfigure(0, weight=1)
        
        # Barra de Busca Local
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


# --- MENU LATERAL DIREITO (Begs, Reps e Peers) ---
        self.frame_begs = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.frame_begs.grid(row=0, column=2, sticky="nsew")
        self.frame_begs.grid_columnconfigure(0, weight=1)
        
        # Faz com que as listas (begs e peers) cresçam para preencher o espaço
        self.frame_begs.grid_rowconfigure(2, weight=1) 
        self.frame_begs.grid_rowconfigure(6, weight=1) 

        # --- SEÇÃO: REPUTAÇÃO ---
        self.lbl_reps = ctk.CTkLabel(self.frame_begs, text=f"Reps: {reps(self.nome_chain)}", font=ctk.CTkFont(size=16, weight="bold"), text_color="MediumPurple2")
        self.lbl_reps.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        # --- SEÇÃO: BEGS ---
        self.titulo_begs = ctk.CTkLabel(self.frame_begs, text="Begs Pendentes", font=ctk.CTkFont(size=16, weight="bold"))
        self.titulo_begs.grid(row=1, column=0, padx=10, pady=(10, 5))

        self.scroll_begs = ctk.CTkScrollableFrame(self.frame_begs, fg_color="transparent")
        self.scroll_begs.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

        self.btn_atualizar_begs = ctk.CTkButton(self.frame_begs, text="Atualizar Begs", fg_color="MediumPurple2", hover_color="MediumPurple4", command=self.carregar_begs)
        self.btn_atualizar_begs.grid(row=3, column=0, padx=10, pady=5)

        # --- SEÇÃO: PEERS (Nova) ---
        # Separador visual
        self.separador = ctk.CTkFrame(self.frame_begs, height=2, fg_color="gray")
        self.separador.grid(row=4, column=0, sticky="ew", padx=20, pady=10)

        self.titulo_peers = ctk.CTkLabel(self.frame_begs, text="Peers (Rede)", font=ctk.CTkFont(size=16, weight="bold"))
        self.titulo_peers.grid(row=5, column=0, padx=10, pady=(5, 5))

        self.scroll_peers = ctk.CTkScrollableFrame(self.frame_begs, fg_color="transparent")
        self.scroll_peers.grid(row=6, column=0, sticky="nsew", padx=10, pady=5)

        # Frame inferior para adicionar novos peers (Entrada + Botão)
        self.frame_add_peer = ctk.CTkFrame(self.frame_begs, fg_color="transparent")
        self.frame_add_peer.grid(row=7, column=0, sticky="ew", padx=10, pady=(5, 20))
        self.frame_add_peer.grid_columnconfigure(0, weight=1)

        self.entry_novo_peer = ctk.CTkEntry(self.frame_add_peer, placeholder_text="Ex: 192.168.0.5:8330", width=150)
        self.entry_novo_peer.grid(row=0, column=0, padx=(0, 5))

        self.btn_add_peer = ctk.CTkButton(self.frame_add_peer, text="+", width=40, fg_color="MediumPurple2", hover_color="MediumPurple4", command=self.evento_adicionar_peer)
        self.btn_add_peer.grid(row=0, column=1)

        self.carregar_begs() # Carrega automaticamente ao iniciar
        self.carregar_peers() # Carrega automaticamente ao iniciar
  
    # eventos!!

    def carregar_begs(self):
        # Limpa os begs atuais da tela
        for widget in self.scroll_begs.winfo_children():
            widget.destroy()
            
        import subprocess
        import json # Necessário para decodificar o payload
        
        try:
            # Lista os blocos que estão no estado de beg
            result = subprocess.run(["freechains", "chain", self.nome_chain, "list", "begs"], capture_output=True, text=True, check=True)
            hashes_begs = result.stdout.strip().split('\n')
            
            tem_begs = False
            for h in hashes_begs:
                if h:
                    tem_begs = True
                    # Busca o conteúdo (payload) de cada beg individualmente
                    try:
                        res_payload = subprocess.run(["freechains", "chain", self.nome_chain, "get", "payload", h], capture_output=True, text=True, check=True)
                        payload = json.loads(res_payload.stdout)
                        titulo = payload.get('titulo', 'Sem título')
                        tags = payload.get('tags', [])
                        link = payload.get('link', '')
                    except Exception:
                        # Se der erro ao ler o payload, evita quebrar a tela inteira
                        titulo = "Erro ao carregar conteúdo"
                        tags = []
                        link = ""
                        
                    # Manda desenhar na tela com os dados completos
                    self.adicionar_item_beg(h, titulo, tags, link)
                    
            if not tem_begs:
                ctk.CTkLabel(self.scroll_begs, text="Nenhum beg.").pack(pady=20)
                
        except Exception as e:
            ctk.CTkLabel(self.scroll_begs, text="Erro ao carregar begs.").pack(pady=20)
            print(f"Erro begs: {e}")

    def adicionar_item_beg(self, hash_id, titulo, tags, link):
        frame_beg = ctk.CTkFrame(self.scroll_begs, fg_color="#2b2b2b")
        frame_beg.pack(fill="x", padx=5, pady=5)

        # 1. Título do Beg (um pouco menor para caber na lateral)
        lbl_titulo = ctk.CTkLabel(frame_beg, text=titulo, font=ctk.CTkFont(size=16, weight="bold"))
        lbl_titulo.pack(anchor="w", padx=10, pady=(10, 0))

        # 2. Tags do Beg
        lbl_tags = ctk.CTkLabel(frame_beg, text=f"Tags: {', '.join(tags)}", text_color="gray", font=ctk.CTkFont(size=12))
        lbl_tags.pack(anchor="w", padx=10, pady=(2, 5))

        # 3. Link do Beg (width=200 para caber no frame de 250px)
        lbl_link = ctk.CTkEntry(frame_beg, width=200) 
        lbl_link.insert(0, link) 
        lbl_link.configure(state="readonly") 
        lbl_link.pack(anchor="w", padx=10, pady=(0, 10))

        # 4. Hash do Beg
        hash_curto = hash_id[:15] + "..."
        lbl_hash = ctk.CTkLabel(frame_beg, text=f"Hash: {hash_curto}", font=ctk.CTkFont(size=10), text_color="darkgray")
        lbl_hash.pack(anchor="w", padx=10, pady=(0, 5))

        # 5. Botão Aprovar
        btn_aprovar = ctk.CTkButton(frame_beg, text="Aprovar (500)", width=150, height=25, fg_color="green", hover_color="darkgreen", command=lambda: self.aprovar_beg(hash_id))
        btn_aprovar.pack(pady=(0, 10))

    def aprovar_beg(self, hash_id):
        recv_peers(self.nome_chain, self.cursor)

        sucesso = gorjeta(hash_id, "500", self.nome_chain)
        if sucesso:
            from sync import reps
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
            # Atualiza o saldo de reps na tela
            self.lbl_reps.configure(text=f"Reps: {reps(self.nome_chain)}")

    def acao_sinalizar(self, hash_id, qtd):
        recv_peers(self.nome_chain, self.cursor)
        sucesso = sinalizacao(hash_id, qtd, self.nome_chain)
        if sucesso:
            # Atualiza o saldo de reps na tela
            self.lbl_reps.configure(text=f"Reps: {reps(self.nome_chain)}")

    def acao_denunciar(self, hash_id, qtd):
        recv_peers(self.nome_chain, self.cursor)
        sucesso = denuncia(hash_id, qtd, self.nome_chain)
        if sucesso:
            # Atualiza o saldo de reps na tela
            self.lbl_reps.configure(text=f"Reps: {reps(self.nome_chain)}")

    def evento_postar(self):
        titulo = self.entry_titulo.get()
        tags_raw = self.entry_tags.get()
        link = self.entry_link.get()
        
        if not titulo or not link:
            print("Preencha título e link!")
            return
            
        tags_lista = [t.strip().lower() for t in tags_raw.split(',') if t.strip()]
        tags_finais = [titulo.lower()] + tags_lista # Primeira tag é o título[cite: 20]

        recv_peers(self.nome_chain, self.cursor)
        
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
            ctk.CTkLabel(self.scroll_feed, text="Nenhum post encontrado.").pack(pady=20)
            return

        # Desenha resultados reais
        for item in resultados:
            hash_do_post = item[0]
            titulo = item[1]
            link = item[2]
            # O ideal é modificar o adicionar_item_feed para receber o hash_do_post também
            self.adicionar_item_feed(hash_do_post, titulo, tags_pesquisa, link)
        
    def adicionar_item_feed(self, hash_id, titulo, tags, link):
        frame_item = ctk.CTkFrame(self.scroll_feed)
        frame_item.pack(fill="x", padx=10, pady=5)
        
        # 1. Título maior em cima
        lbl_titulo = ctk.CTkLabel(frame_item, text=titulo, font=ctk.CTkFont(size=20, weight="bold"))
        lbl_titulo.pack(anchor="w", padx=10, pady=(10, 0))

        # 2. Tags pequenas embaixo do título
        lbl_tags = ctk.CTkLabel(frame_item, text=f"Tags: {', '.join(tags)}", text_color="gray", font=ctk.CTkFont(size=12))
        lbl_tags.pack(anchor="w", padx=10, pady=(2, 10))

        # 3. Link médio no meio para ser copiado (Correção do CTkEntry)
        lbl_link = ctk.CTkEntry(frame_item, width=400) # Largura ajustada para tamanho "médio"
        lbl_link.insert(0, link) # Insere o link primeiro
        lbl_link.configure(state="readonly") # Bloqueia para leitura depois de inserir
        lbl_link.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Frame para botões de Reputação
        frame_reps = ctk.CTkFrame(frame_item, fg_color="transparent")
        frame_reps.pack(fill="x", padx=10, pady=(0, 10))
        
        # 4. Campo de entrada para a quantia
        entry_qtd = ctk.CTkEntry(frame_reps, width=60, placeholder_text="Qtd")
        entry_qtd.pack(side="left", padx=(0, 10))
        
        # 5. Botões com tamanhos diferentes e conectados às ações
        # Botão médio
        btn_tip = ctk.CTkButton(frame_reps, text="Gorjeta", width=120, fg_color="green", hover_color="darkgreen",
                                command=lambda: self.acao_gorjeta(hash_id, entry_qtd.get()))
        btn_tip.pack(side="left", padx=(0, 10))
        
        # Botões pequenos
        btn_sinalizar = ctk.CTkButton(frame_reps, text="Sinalizar", width=80, fg_color="#d48806", hover_color="#ad6e02",
                                      command=lambda: self.acao_sinalizar(hash_id, entry_qtd.get()))
        btn_sinalizar.pack(side="left", padx=(0, 10))

        btn_denunciar = ctk.CTkButton(frame_reps, text="Denunciar", width=80, fg_color="red", hover_color="darkred",
                                      command=lambda: self.acao_denunciar(hash_id, entry_qtd.get()))
        btn_denunciar.pack(side="left")

    def carregar_peers(self):
        # Limpa os peers atuais da tela
        for widget in self.scroll_peers.winfo_children():
            widget.destroy()
            
        try:
            # Busca todos os peers cadastrados na tabela SQLite
            self.cursor.execute("SELECT endereco FROM Peers")
            lista_peers = self.cursor.fetchall()
            
            if not lista_peers:
                ctk.CTkLabel(self.scroll_peers, text="Nenhum peer cadastrado.", text_color="gray").pack(pady=20)
                return
                
            for peer in lista_peers:
                endereco = peer[0] # fetchall retorna uma lista de tuplas
                self.adicionar_item_peer(endereco)
                
        except Exception as e:
            ctk.CTkLabel(self.scroll_peers, text="Erro ao carregar peers.", text_color="red").pack(pady=20)
            print(f"[GUI] Erro ao listar peers: {e}")

    def adicionar_item_peer(self, endereco):
            # Cria um bloco visual para cada peer
            frame_peer = ctk.CTkFrame(self.scroll_peers, fg_color="#2b2b2b")
            frame_peer.pack(fill="x", padx=5, pady=2)
            
            lbl_endereco = ctk.CTkLabel(frame_peer, text=endereco, font=ctk.CTkFont(size=12))
            lbl_endereco.pack(side="left", padx=10, pady=5)
            
            # (Opcional) Poderíamos adicionar um botão "X" aqui para deletar o peer futuramente

    def evento_adicionar_peer(self):
            novo_peer = self.entry_novo_peer.get().strip()
            
            if not novo_peer:
                return
                
            try:
                # Tenta inserir o peer na tabela do banco de dados
                from sync import add_peer_db
                # Nota: a função add_peer_db já está definida no seu arquivo sync.py original
                add_peer_db(novo_peer, self.conn, self.cursor)
                
                # Limpa a caixa de texto
                self.entry_novo_peer.delete(0, 'end')
                
                # Recarrega a lista para mostrar o novo peer
                self.carregar_peers()
                
            except Exception as e:
                # Pode falhar se for duplicado, pois a coluna endereco é UNIQUE no SQLite
                print(f"[GUI] Falha ao adicionar peer (já existe ou erro SQL): {e}")
                self.entry_novo_peer.delete(0, 'end')
                self.entry_novo_peer.insert(0, "Erro/Duplicado")