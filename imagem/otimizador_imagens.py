import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import os

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class OtimizadorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TLG Otimizador de Imagens Py (Fast)")
        self.geometry("750x850")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- 1. SELEÇÃO DA FONTE ---
        self.btn_pasta = ctk.CTkButton(self, text="Selecionar Pasta de Origem", command=self.selecionar_pasta)
        self.btn_pasta.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        self.lbl_caminho = ctk.CTkLabel(self, text="Nenhuma pasta selecionada", text_color="gray")
        self.lbl_caminho.grid(row=1, column=0, padx=20, pady=(0, 5))

        # --- 2. LISTA DE IMAGENS ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Imagens Encontradas", height=200)
        self.scroll_frame.grid(row=2, column=0, padx=20, pady=5, sticky="nsew")
        self.checkboxes_imagens = [] 

        # --- 3. CONFIGURAÇÕES ---
        self.frame_config = ctk.CTkFrame(self)
        self.frame_config.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        # Qualidade
        self.lbl_qualidade = ctk.CTkLabel(self.frame_config, text="Qualidade: 80%")
        self.lbl_qualidade.pack(anchor="w", padx=10, pady=(10,0))
        
        # O slider agora apenas atualiza o texto visual, sem processamento pesado
        self.slider_qualidade = ctk.CTkSlider(self.frame_config, from_=10, to=100, command=self.evento_slider)
        self.slider_qualidade.set(80)
        self.slider_qualidade.pack(fill="x", padx=10, pady=5)

        # Formato
        self.lbl_formato = ctk.CTkLabel(self.frame_config, text="Formato de Saída:", font=("Arial", 12, "bold"))
        self.lbl_formato.pack(anchor="w", padx=10, pady=(10, 5))

        self.frame_radios = ctk.CTkFrame(self.frame_config, fg_color="transparent")
        self.frame_radios.pack(fill="x", padx=10, pady=(0, 5))

        self.var_formato = ctk.StringVar(value="Manter Original")
        opcoes_formato = ["Manter Original", "JPG", "PNG", "WEBP"]
        for op in opcoes_formato:
            # Removido o command=self.calcular_estimativa
            rb = ctk.CTkRadioButton(self.frame_radios, text=op, variable=self.var_formato, value=op)
            rb.pack(side="left", padx=10)

        # REDIMENSIONAMENTO (RESIZE)
        self.lbl_resize = ctk.CTkLabel(self.frame_config, text="Redimensionamento:", font=("Arial", 12, "bold"))
        self.lbl_resize.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.frame_resize_opts = ctk.CTkFrame(self.frame_config, fg_color="transparent")
        self.frame_resize_opts.pack(fill="x", padx=10, pady=(0, 10))

        self.var_resize_mode = ctk.StringVar(value="Original")

        # Opções de Resize (Apenas atualizam a UI para habilitar/desabilitar campos)
        self.rb_size_orig = ctk.CTkRadioButton(self.frame_resize_opts, text="Manter Tamanho", variable=self.var_resize_mode, value="Original", command=self.atualizar_ui_resize)
        self.rb_size_orig.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.rb_size_pct = ctk.CTkRadioButton(self.frame_resize_opts, text="Reduzir (%)", variable=self.var_resize_mode, value="Percent", command=self.atualizar_ui_resize)
        self.rb_size_pct.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        self.combo_pct = ctk.CTkComboBox(self.frame_resize_opts, values=["10%", "25%", "50%", "75%", "90%"], width=100)
        self.combo_pct.grid(row=1, column=1, padx=10, sticky="w")
        self.combo_pct.set("50%")

        self.rb_size_px = ctk.CTkRadioButton(self.frame_resize_opts, text="Máximo (Px)", variable=self.var_resize_mode, value="Pixel", command=self.atualizar_ui_resize)
        self.rb_size_px.grid(row=2, column=0, sticky="w", padx=10, pady=5)

        self.frame_inputs_px = ctk.CTkFrame(self.frame_resize_opts, fg_color="transparent")
        self.frame_inputs_px.grid(row=2, column=1, sticky="w")

        self.entry_w = ctk.CTkEntry(self.frame_inputs_px, placeholder_text="Larg. Max", width=80)
        self.entry_w.pack(side="left", padx=5)
        self.entry_h = ctk.CTkEntry(self.frame_inputs_px, placeholder_text="Alt. Auto", width=80)
        self.entry_h.pack(side="left", padx=5)
        
        # Label Informativa (Estática agora)
        self.lbl_info = ctk.CTkLabel(self.frame_config, text="Configure as opções acima e clique em Iniciar", text_color="gray")
        self.lbl_info.pack(pady=10)

        # --- 4. AÇÃO ---
        self.btn_otimizar = ctk.CTkButton(self, text="INICIAR OTIMIZAÇÃO", command=self.iniciar_otimizacao, fg_color="green", hover_color="darkgreen", height=40)
        self.btn_otimizar.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.barra_progresso = ctk.CTkProgressBar(self)
        self.barra_progresso.set(0)
        self.barra_progresso.grid(row=5, column=0, padx=20, pady=(0, 10), sticky="ew")

        # --- 5. LOG ---
        self.txt_log = ctk.CTkTextbox(self, height=100)
        self.txt_log.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.txt_log.insert("0.0", "Aguardando início...\n")

        self.caminho_atual = ""
        self.atualizar_ui_resize() 

    # --- UI EVENTOS (LEVES) ---
    def atualizar_ui_resize(self):
        """Apenas habilita ou desabilita campos, sem cálculos."""
        modo = self.var_resize_mode.get()
        
        if modo == "Percent":
            self.combo_pct.configure(state="normal")
        else:
            self.combo_pct.configure(state="disabled")
            
        if modo == "Pixel":
            self.entry_w.configure(state="normal")
            self.entry_h.configure(state="normal")
        else:
            self.entry_w.configure(state="disabled")
            self.entry_h.configure(state="disabled")

    def evento_slider(self, val):
        """Apenas atualiza o texto do label."""
        self.lbl_qualidade.configure(text=f"Qualidade: {int(val)}%")

    def selecionar_pasta(self):
        pasta = filedialog.askdirectory()
        if pasta:
            self.caminho_atual = pasta
            self.lbl_caminho.configure(text=pasta)
            self.carregar_imagens()

    def carregar_imagens(self):
        # 1. Limpa a lista visual antiga
        for cb in self.checkboxes_imagens: cb.destroy()
        self.checkboxes_imagens.clear()
        
        # 2. Lista de extensões ampliada
        # Adicionei BMP, TIFF e garantimos que verifique maiúsculas/minúsculas
        exts = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.ico')
        imagens_encontradas = []

        self.log_msg(f"Lendo pasta: {self.caminho_atual}...")

        try:
            # 3. MUDANÇA PRINCIPAL: os.walk em vez de os.listdir
            # Isso permite entrar em subpastas automaticamente
            for root, dirs, files in os.walk(self.caminho_atual):
                for arquivo in files:
                    if arquivo.lower().endswith(exts):
                        # Cria o caminho completo e o relativo para exibição
                        caminho_completo = os.path.join(root, arquivo)
                        
                        # Pega apenas o caminho relativo à pasta base (ex: "Subpasta\foto.jpg")
                        caminho_relativo = os.path.relpath(caminho_completo, self.caminho_atual)
                        
                        imagens_encontradas.append(caminho_relativo)

            # 4. Verifica se achou algo
            if not imagens_encontradas:
                self.log_msg("AVISO: Nenhuma imagem encontrada nesta pasta (nem nas subpastas).")
                return

            # 5. Ordena alfabeticamente para ficar bonitinho
            imagens_encontradas.sort()

            # 6. Cria os checkboxes
            # Limitamos a exibir no máximo 500 imagens para não travar a interface se houver milhares
            limite_exibicao = 500
            for i, caminho_rel in enumerate(imagens_encontradas):
                if i >= limite_exibicao:
                    self.log_msg(f"AVISO: Exibindo apenas as primeiras {limite_exibicao} imagens (de {len(imagens_encontradas)}).")
                    break
                    
                cb = ctk.CTkCheckBox(self.scroll_frame, text=caminho_rel)
                cb.pack(anchor="w", padx=5, pady=2)
                cb.select()
                self.checkboxes_imagens.append(cb)
            
            self.log_msg(f"Sucesso: {len(imagens_encontradas)} imagens carregadas.")

        except PermissionError:
            self.log_msg("ERRO CRÍTICO: Sem permissão para ler esta pasta. Tente executar como Administrador.")
            messagebox.showerror("Erro de Permissão", "O Windows bloqueou a leitura desta pasta.\nTente mover as imagens para uma pasta pública ou executar o programa como Admin.")
        
        except Exception as e:
            self.log_msg(f"ERRO DESCONHECIDO: {e}")
            print(e) # Imprime no terminal para debug

    # --- PROCESSAMENTO REAL (SÓ RODA AO CLICAR NO BOTÃO) ---
    def processar_imagem_pil(self, img_original):
        img = img_original.copy()
        w_orig, h_orig = img.size
        modo = self.var_resize_mode.get()

        if modo == "Percent":
            # (Código da percentagem que já corrigimos antes...)
            str_pct = self.combo_pct.get().replace("%", "")
            if str_pct.isdigit():
                porcentagem_reducao = int(str_pct) / 100.0
                fator_final = 1.0 - porcentagem_reducao
                if fator_final <= 0: fator_final = 0.01
                novos_w = int(w_orig * fator_final)
                novos_h = int(h_orig * fator_final)
                novos_w = max(1, novos_w)
                novos_h = max(1, novos_h)
                img = img.resize((novos_w, novos_h), Image.Resampling.LANCZOS)

        elif modo == "Pixel":
            try:
                # Obtém os valores removendo espaços vazios
                val_w = self.entry_w.get().strip()
                val_h = self.entry_h.get().strip()

                # CENÁRIO 1: Apenas LARGURA definida (Altura Auto)
                if val_w and not val_h:
                    target_w = int(val_w)
                    # Regra de 3 para manter proporção: (NovoW / VelhoW) * VelhoH
                    ratio = target_w / w_orig
                    target_h = int(h_orig * ratio)
                    img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)

                # CENÁRIO 2: Apenas ALTURA definida (Largura Auto)
                elif val_h and not val_w:
                    target_h = int(val_h)
                    ratio = target_h / h_orig
                    target_w = int(w_orig * ratio)
                    img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)

                # CENÁRIO 3: AMBOS definidos (Funciona como Limite Máximo)
                elif val_w and val_h:
                    max_w = int(val_w)
                    max_h = int(val_h)
                    img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)

            except ValueError:
                pass # Se digitar letras ou erro, ignora e mantém original

        return img

    def iniciar_otimizacao(self):
        if not self.caminho_atual: 
            messagebox.showwarning("Aviso", "Selecione uma pasta primeiro!")
            return
            
        selecionados = [cb.cget("text") for cb in self.checkboxes_imagens if cb.get() == 1]
        if not selecionados: 
            messagebox.showwarning("Aviso", "Nenhuma imagem selecionada!")
            return

        pasta_destino_raiz = os.path.join(self.caminho_atual, "Otimizadas")
        # Não precisamos criar a raiz aqui, o comando dentro do loop vai criar tudo

        self.txt_log.delete("0.0", "end")
        self.log_msg(f"--- Iniciando Otimização de {len(selecionados)} imagens ---")
        
        sucessos, erros, bytes_totais_orig, bytes_totais_final = 0, 0, 0, 0
        total_imgs = len(selecionados)

        for i, nome_arq in enumerate(selecionados):
            try:
                caminho_completo = os.path.join(self.caminho_atual, nome_arq)
                tamanho_arq_orig = os.path.getsize(caminho_completo) # Pega tamanho mas não soma ao total ainda
                
                img = Image.open(caminho_completo)
                
                # 1. Aplica Redimensionamento
                img = self.processar_imagem_pil(img)

                # 2. Define Formato
                nome_sem_ext, ext = os.path.splitext(nome_arq)
                formato = self.var_formato.get()
                
                if formato == "Manter Original": 
                    ext_final = ext
                    fmt_salvar = None
                else:
                    ext_final = f".{formato.lower()}"
                    fmt_salvar = formato
                    if fmt_salvar == "JPG": fmt_salvar = "JPEG"
                    if fmt_salvar == "JPEG" and img.mode in ("RGBA", "P"): img = img.convert("RGB")

                # Define caminho de saída mantendo estrutura de pastas
                saida = os.path.join(pasta_destino_raiz, f"{nome_sem_ext}_otim{ext_final}")
                
                # --- CORREÇÃO DO ERRO ---
                # Verifica se a subpasta de destino existe, se não, cria.
                pasta_saida = os.path.dirname(saida)
                os.makedirs(pasta_saida, exist_ok=True)
                # ------------------------

                # 3. Salva no Disco
                img.save(saida, optimize=True, quality=int(self.slider_qualidade.get()), format=fmt_salvar)
                
                # Só soma nas estatísticas se deu certo chegar até aqui
                bytes_totais_orig += tamanho_arq_orig
                bytes_totais_final += os.path.getsize(saida)
                
                self.log_msg(f"OK: {nome_arq}")
                sucessos += 1

            except Exception as e:
                self.log_msg(f"ERRO {nome_arq}: {e}")
                erros += 1
            
            # Atualiza barra de progresso
            self.barra_progresso.set((i+1)/total_imgs)
            self.update()

        # Relatório Final
        if bytes_totais_orig > 0:
            mb_econ = (bytes_totais_orig - bytes_totais_final) / 1024 / 1024
        else:
            mb_econ = 0

        msg_final = (f"Finalizado!\n"
                     f"Sucessos: {sucessos} | Erros: {erros}\n"
                     f"Economia Real: {mb_econ:.2f} MB")
        
        self.log_msg("-" * 30)
        self.log_msg(msg_final)
        messagebox.showinfo("Concluído", msg_final)

    def log_msg(self, msg):
        self.txt_log.insert("end", msg + "\n")
        self.txt_log.see("end")

    def formatar_tamanho(self, b):
        for u in ['B', 'KB', 'MB']:
            if b < 1024: return f"{b:.1f} {u}"
            b /= 1024
        return f"{b:.1f} GB"

if __name__ == "__main__":
    app = OtimizadorApp()
    app.mainloop()
