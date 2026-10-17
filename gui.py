import customtkinter as ctk
from sync import enviar_post, sinalizacao, gorjeta, denuncia, iniciar_chain, busca

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
        
        self.lbl_info = ctk.CTkLabel(self, text=f"Como iniciar a #torrents?", font=ctk.CTkFont(weight="bold", size=16))
        self.lbl_info.pack(pady=(30, 20))
        
        # Botão 1: Criar do zero
        self.btn_criar = ctk.CTkButton(self, text="Criar Cadeia Local (Nó Zero)", command=self.criar_zero, fg_color="purple")
        self.btn_criar.pack(pady=10)
        
        # Botão 2: Clonar de Peer
        self.frame_clone = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_clone.pack(pady=10)
        
        self.entry_peer = ctk.CTkEntry(self.frame_clone, placeholder_text="IP do Colega (ex: 192.168.1.5:8333)", width=220)
        self.entry_peer.pack(side="left", padx=(0, 10))
        
        self.btn_clone = ctk.CTkButton(self.frame_clone, text="Clonar", command=self.clonar_peer, fg_color="purple",width=80)
        self.btn_clone.pack(side="left")

    def criar_zero(self):
        if iniciar_chain(self.nome_chain): # Chama função do sync.py
            self.destroy() # Se deu certo, fecha essa janela para a principal abrir

    def clonar_peer(self):
        peer = self.entry_peer.get().strip()
        if peer:
            if iniciar_chain(self.nome_chain, peer): # Clona do IP digitado
                self.destroy()

class AppGUI(ctk.CTk):
    def __init__(self, nome_chain, cursor):
        super().__init__()

        self.nome_chain = nome_chain # define como self para diminuir parametros
        self.cursor = cursor

        self.title("LinkChains")
        self.geometry("900x600")
        try:
            self.iconbitmap("freechains_logo.ico")
        except Exception:
            pass

        # Grid layout da janela principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # --- MENU LATERAL (Envio de Conteúdo) ---
        self.frame_lateral = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.frame_lateral.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.frame_lateral, text="Post Novo", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.entry_titulo = ctk.CTkEntry(self.frame_lateral, placeholder_text="Título do Arquivo")
        self.entry_titulo.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # O padrão exige envio das tags para descrever o conteúdo[cite: 7]
        self.entry_tags = ctk.CTkEntry(self.frame_lateral, placeholder_text="Tags (separadas por vírgula)")
        self.entry_tags.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.entry_link = ctk.CTkEntry(self.frame_lateral, placeholder_text="Magnet Link...")
        self.entry_link.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_enviar = ctk.CTkButton(self.frame_lateral, text="Postar Conteúdo",fg_color="purple", command=self.evento_postar)
        self.btn_enviar.grid(row=4, column=0, padx=20, pady=20)
        
        # --- ÁREA PRINCIPAL (Busca e Feed) ---
        self.frame_principal = ctk.CTkFrame(self)
        self.frame_principal.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.frame_principal.grid_rowconfigure(1, weight=1)
        self.frame_principal.grid_columnconfigure(0, weight=1)
        
        # Barra de Busca Local
        self.frame_busca = ctk.CTkFrame(self.frame_principal, fg_color="transparent")
        self.frame_busca.grid(row=0, column=0, sticky="ew")
        self.frame_busca.grid_columnconfigure(0, weight=1)
        
        self.entry_busca = ctk.CTkEntry(self.frame_busca, placeholder_text="Buscar por tags (Ex: terror, filmes)...")
        self.entry_busca.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="ew")
        
        self.btn_buscar = ctk.CTkButton(self.frame_busca, text="Buscar", fg_color="purple", command=self.evento_buscar)
        self.btn_buscar.grid(row=0, column=1, pady=10)
        
        # Feed de Conteúdo (Scrollable)
        self.scroll_feed = ctk.CTkScrollableFrame(self.frame_principal, label_text="Conteúdos Encontrados")
        self.scroll_feed.grid(row=1, column=0, sticky="nsew")

    # eventos!!

    def evento_postar(self):
        titulo = self.entry_titulo.get()
        tags_raw = self.entry_tags.get()
        link = self.entry_link.get()
        
        if not titulo or not link:
            print("Preencha título e link!")
            return
            
        tags_lista = [t.strip().lower() for t in tags_raw.split(',') if t.strip()]
        tags_finais = [titulo.lower()] + tags_lista # Primeira tag é o título[cite: 20]
        
        sucesso = enviar_post(titulo, tags_finais, link, self.nome_chain)
        if sucesso:
            self.entry_titulo.delete(0, 'end')
            self.entry_tags.delete(0, 'end')
            self.entry_link.delete(0, 'end')

    def evento_buscar(self):
        termo = self.entry_busca.get()
        tags_pesquisa = [t.strip().lower() for t in termo.split(',') if t.strip()]
        
        for widget in self.scroll_feed.winfo_children():
            widget.destroy()
            
        resultados = busca(tags_pesquisa, self.cursor)
        
        if not resultados:
            ctk.CTkLabel(self.scroll_feed, text="Nenhum arquivo encontrado.").pack(pady=20)
            return

        # Desenha resultados reais
        for item in resultados:
            hash_do_post = item[0]
            titulo = item[1]
            link = item[2]
            # O ideal é modificar o adicionar_item_feed para receber o hash_do_post também
            self.adicionar_item_feed(hash_do_post, titulo, tags_pesquisa, link)
        
    def adicionar_item_feed(self, titulo, tags, link):
        frame_item = ctk.CTkFrame(self.scroll_feed)
        frame_item.pack(fill="x", padx=10, pady=5)
        
        lbl_titulo = ctk.CTkLabel(frame_item, text=titulo, font=ctk.CTkFont(weight="bold"))
        lbl_titulo.pack(anchor="w", padx=10, pady=(10, 0))
        
        lbl_tags = ctk.CTkLabel(frame_item, text=f"Tags: {', '.join(tags)}", text_color="gray")
        lbl_tags.pack(anchor="w", padx=10)
        
        # Botões de Reputação
        frame_reps = ctk.CTkFrame(frame_item, fg_color="transparent")
        frame_reps.pack(fill="x", padx=10, pady=10)
        
        btn_tip = ctk.CTkButton(frame_reps, text="Gorjeta (+Reps)", width=120, fg_color="green", hover_color="darkgreen")
        btn_tip.pack(side="left", padx=(0, 10)) # Opcional para bom conteúdo[cite: 24]
        
        btn_denunciar = ctk.CTkButton(frame_reps, text="Denunciar (-Reps)", width=120, fg_color="red", hover_color="darkred")
        btn_denunciar.pack(side="left") # Recomendado para spam/conteúdo malicioso[cite: 25]
