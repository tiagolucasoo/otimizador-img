import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import os
import io

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class OtimizadorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TLG Otimizador de Imagens Py")
        self.geometry("750x850")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.btn_pasta = ctk.CTkButton(self, text="Selecionar Pasta de Origem", command=self.selecionar_pasta)
        self.btn_pasta.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        self.lbl_caminho = ctk.CTkLabel(self, text="Nenhuma pasta selecionada", text_color="gray")
        self.lbl_caminho.grid(row=1, column=0, padx=20, pady=(0, 5))

        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Imagens Encontradas", height=200)
        self.scroll_frame.grid(row=2, column=0, padx=20, pady=5, sticky="nsew")
        self.checkboxes_imagens = [] 

        self.frame_config = ctk.CTkFrame(self)
        self.frame_config.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.lbl_qualidade = ctk.CTkLabel(self.frame_config, text="Qualidade: 80%")
        self.lbl_qualidade.pack(anchor="w", padx=10, pady=(10,0))
        
        self.slider_qualidade = ctk.CTkSlider(self.frame_config, from_=10, to=100, command=self.evento_slider)
        self.slider_qualidade.set(80)
        self.slider_qualidade.pack(fill="x", padx=10, pady=5)

        self.lbl_formato = ctk.CTkLabel(self.frame_config, text="Formato de Saída:", font=("Arial", 12, "bold"))
        self.lbl_formato.pack(anchor="w", padx=10, pady=(10, 5))

        self.frame_radios = ctk.CTkFrame(self.frame_config, fg_color="transparent")
        self.frame_radios.pack(fill="x", padx=10, pady=(0, 5))

        self.var_formato = ctk.StringVar(value="Manter Original")
        opcoes_formato = ["Manter Original", "JPG", "PNG", "WEBP"]
        for op in opcoes_formato:
            rb = ctk.CTkRadioButton(self.frame_radios, text=op, variable=self.var_formato, value=op, command=self.calcular_estimativa)
            rb.pack(side="left", padx=10)

        
        # REDIMENSIONAMENTO (RESIZE)
        
        self.lbl_resize = ctk.CTkLabel(self.frame_config, text="Redimensionamento:", font=("Arial", 12, "bold"))
        self.lbl_resize.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.frame_resize_opts = ctk.CTkFrame(self.frame_config, fg_color="transparent")
        self.frame_resize_opts.pack(fill="x", padx=10, pady=(0, 10))

        self.var_resize_mode = ctk.StringVar(value="Original")

        # Tamanho
        self.rb_size_orig = ctk.CTkRadioButton(self.frame_resize_opts, text="Manter Tamanho", variable=self.var_resize_mode, value="Original", command=self.atualizar_ui_resize)
        self.rb_size_orig.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        # Porcentagem
        self.rb_size_pct = ctk.CTkRadioButton(self.frame_resize_opts, text="Reduzir (%)", variable=self.var_resize_mode, value="Percent", command=self.atualizar_ui_resize)
        self.rb_size_pct.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        self.combo_pct = ctk.CTkComboBox(self.frame_resize_opts, values=["10%", "25%", "50%", "75%", "90%"], width=100, command=self.evento_combo_pct)
        self.combo_pct.grid(row=1, column=1, padx=10, sticky="w")
        self.combo_pct.set("50%")

        # Dimensões
        self.rb_size_px = ctk.CTkRadioButton(self.frame_resize_opts, text="Máximo (Px)", variable=self.var_resize_mode, value="Pixel", command=self.atualizar_ui_resize)
        self.rb_size_px.grid(row=2, column=0, sticky="w", padx=10, pady=5)

        self.frame_inputs_px = ctk.CTkFrame(self.frame_resize_opts, fg_color="transparent")
        self.frame_inputs_px.grid(row=2, column=1, sticky="w")

        self.entry_w = ctk.CTkEntry(self.frame_inputs_px, placeholder_text="Larg. Max", width=80)
        self.entry_w.pack(side="left", padx=5)
        self.entry_h = ctk.CTkEntry(self.frame_inputs_px, placeholder_text="Alt. Max", width=80)
        self.entry_h.pack(side="left", padx=5)
        
        # Estimativa
        self.entry_w.bind("<KeyRelease>", lambda event: self.calcular_estimativa())
        self.entry_h.bind("<KeyRelease>", lambda event: self.calcular_estimativa())

        self.lbl_estimativa = ctk.CTkLabel(self.frame_config, text="Selecione uma imagem para ver a estimativa", text_color="#4ea8de")
        self.lbl_estimativa.pack(pady=10)

        # Otimização
        self.btn_otimizar = ctk.CTkButton(self, text="INICIAR OTIMIZAÇÃO", command=self.iniciar_otimizacao, fg_color="green", hover_color="darkgreen", height=40)
        self.btn_otimizar.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.barra_progresso = ctk.CTkProgressBar(self)
        self.barra_progresso.set(0)
        self.barra_progresso.grid(row=5, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Status
        self.txt_log = ctk.CTkTextbox(self, height=100)
        self.txt_log.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.txt_log.insert("0.0", "Aguardando...\n")

        self.caminho_atual = ""
        self.atualizar_ui_resize() # Configurar estado inicial

    def atualizar_ui_resize(self):
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

        self.calcular_estimativa()

    def evento_combo_pct(self, choice):
        self.calcular_estimativa()

    def processar_imagem_pil(self, img_original):
        img = img_original.copy()
        w, h = img.size
        modo = self.var_resize_mode.get()

        if modo == "Percent":
            str_pct = self.combo_pct.get().replace("%", "")
            if str_pct.isdigit():
                fator = int(str_pct) / 100.0
                novos_w = int(w * fator)
                novos_h = int(h * fator)
                img = img.resize((novos_w, novos_h), Image.Resampling.LANCZOS)

        elif modo == "Pixel":
            try:
                max_w = int(self.entry_w.get()) if self.entry_w.get() else 99999
                max_h = int(self.entry_h.get()) if self.entry_h.get() else 99999
                img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
            except ValueError:
                pass

        return img

    def calcular_estimativa(self):
        if not self.caminho_atual or not self.checkboxes_imagens: return
        imagem_alvo = next((cb.cget("text") for cb in self.checkboxes_imagens if cb.get() == 1), None)
        if not imagem_alvo: return

        try:
            caminho = os.path.join(self.caminho_atual, imagem_alvo)
            tamanho_original = os.path.getsize(caminho)
            img = Image.open(caminho)
            
            img = self.processar_imagem_pil(img)
            
            qualidade = int(self.slider_qualidade.get())
            formato = self.var_formato.get()
            
            if formato == "Manter Original": formato_salvar = img.format
            else: 
                formato_salvar = formato
                if formato_salvar == "JPG": formato_salvar = "JPEG"
                if formato_salvar == "JPEG" and img.mode in ("RGBA", "P"): img = img.convert("RGB")

            buffer = io.BytesIO()
            img.save(buffer, format=formato_salvar, optimize=True, quality=qualidade)
            tamanho_final = buffer.tell()

            reducao = 100 - (tamanho_final / tamanho_original * 100)
            self.lbl_estimativa.configure(
                text=f"Previsão: {img.width}x{img.height}px | {self.formatar_tamanho(tamanho_original)} ➜ {self.formatar_tamanho(tamanho_final)} (-{reducao:.0f}%)"
            )
        except Exception as e:
            self.lbl_estimativa.configure(text=f"Erro na estimativa: {str(e)}")

    def iniciar_otimizacao(self):
        if not self.caminho_atual: return
        selecionados = [cb.cget("text") for cb in self.checkboxes_imagens if cb.get() == 1]
        if not selecionados: return

        pasta_destino = os.path.join(self.caminho_atual, "Otimizadas")
        if not os.path.exists(pasta_destino): os.makedirs(pasta_destino)

        self.txt_log.delete("0.0", "end")
        self.log_msg(f"Iniciando {len(selecionados)} imagens...")
        
        sucessos, erros, bytes_orig, bytes_final = 0, 0, 0, 0

        for i, nome_arq in enumerate(selecionados):
            try:
                caminho = os.path.join(self.caminho_atual, nome_arq)
                bytes_orig += os.path.getsize(caminho)
                
                img = Image.open(caminho)
                img = self.processar_imagem_pil(img)
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

                saida = os.path.join(pasta_destino, f"{nome_sem_ext}_otim{ext_final}")
                img.save(saida, optimize=True, quality=int(self.slider_qualidade.get()), format=fmt_salvar)
                
                bytes_final += os.path.getsize(saida)
                self.log_msg(f"OK: {nome_arq}")
                sucessos += 1

            except Exception as e:
                self.log_msg(f"ERRO {nome_arq}: {e}")
                erros += 1
            
            self.barra_progresso.set((i+1)/len(selecionados))
            self.update()

        mb_econ = (bytes_orig - bytes_final) / 1024 / 1024
        msg_final = f"Fim! Economia de {mb_econ:.2f} MB em {sucessos} arquivos."
        self.log_msg(msg_final)
        messagebox.showinfo("Concluído", msg_final)

    def log_msg(self, msg):
        self.txt_log.insert("end", msg + "\n")
        self.txt_log.see("end")

    def selecionar_pasta(self):
        pasta = filedialog.askdirectory()
        if pasta:
            self.caminho_atual = pasta
            self.lbl_caminho.configure(text=pasta)
            self.carregar_imagens()
            self.calcular_estimativa()

    def carregar_imagens(self):
        for cb in self.checkboxes_imagens: cb.destroy()
        self.checkboxes_imagens.clear()
        try:
            exts = ('.jpg', '.jpeg', '.png', '.webp')
            arqs = [f for f in os.listdir(self.caminho_atual) if f.lower().endswith(exts)]
            for arq in arqs:
                cb = ctk.CTkCheckBox(self.scroll_frame, text=arq)
                cb.pack(anchor="w", padx=5)
                cb.select()
                self.checkboxes_imagens.append(cb)
        except: pass
        
    def evento_slider(self, val):
        self.lbl_qualidade.configure(text=f"Qualidade: {int(val)}%")
        self.calcular_estimativa()

    def formatar_tamanho(self, b):
        for u in ['B', 'KB', 'MB']:
            if b < 1024: return f"{b:.1f} {u}"
            b /= 1024
        return f"{b:.1f} GB"

if __name__ == "__main__":
    app = OtimizadorApp()
    app.mainloop()