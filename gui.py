import customtkinter as ctk
from sync import enviar_post_rede 

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AppGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("LinkChains")
        self.geometry("900x600")
        
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
        
        self.btn_enviar = ctk.CTkButton(self.frame_lateral, text="Postar Conteúdo", command=self.evento_postar)
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
        
        self.btn_buscar = ctk.CTkButton(self.frame_busca, text="Buscar", command=self.evento_buscar)
        self.btn_buscar.grid(row=0, column=1, pady=10)
        
        # Feed de Conteúdo (Scrollable)
        self.scroll_feed = ctk.CTkScrollableFrame(self.frame_principal, label_text="Conteúdos Encontrados")
        self.scroll_feed.grid(row=1, column=0, sticky="nsew")

    # --- 3. EVENTOS DOS BOTÕES ---

    def evento_postar(self):
        titulo = self.entry_titulo.get()
        tags_raw = self.entry_tags.get()
        link = self.entry_link.get()
        
        if not titulo or not link:
            print("Preencha título e link!")
            return
            
        tags_lista = [t.strip().lower() for t in tags_raw.split(',') if t.strip()]
        tags_finais = [titulo.lower()] + tags_lista # Primeira tag é o título[cite: 20]
        
        sucesso = enviar_post_rede(titulo, tags_finais, link)
        if sucesso:
            self.entry_titulo.delete(0, 'end')
            self.entry_tags.delete(0, 'end')
            self.entry_link.delete(0, 'end')

    def evento_buscar(self):
        termo = self.entry_busca.get()
        print(f"Executando pattern-matching local para: {termo}") # Busca ocorre do lado da aplicação[cite: 21]
        
        # Limpa os resultados anteriores do feed
        for widget in self.scroll_feed.winfo_children():
            widget.destroy()
            
        # (Aqui você chama a query do SQLite com 'HAVING COUNT' discutida antes)
        # Simulando resultados visuais
        self.adicionar_item_feed("O Iluminado", ["terror", "filmes", "kubrick"], "magnet:?xt=urn...")
        
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
