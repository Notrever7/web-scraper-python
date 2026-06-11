import tkinter as tk
from tkinter import font as tkfont, filedialog, messagebox, ttk
import csv
import os
import threading

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Biblioteca não encontrada",
        f"Erro: {e}\n\n"
        "Abra o cmd e rode:\n"
        "pip install requests beautifulsoup4"
    )
    root.destroy()
    exit()

# ════════════════════════════════════════
#  CORES
# ════════════════════════════════════════

CORES = {
    "bg": "#0f0f13",
    "surface": "#1a1a24",
    "border": "#2a2a3a",
    "accent": "#7c6cfc",
    "accent2": "#4cc9f0",
    "accent3": "#f72585",
    "correct": "#3ddc84",
    "wrong": "#ff5c5c",
    "text": "#e8e8f0",
    "muted": "#7a7a9a",
    "input_bg": "#151520",
}


# ════════════════════════════════════════
#  CLASSE PRINCIPAL
# ════════════════════════════════════════

class ScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Scraper — Extrator de Dados")
        self.root.configure(bg=CORES["bg"])

        largura, altura = 960, 700
        x = (self.root.winfo_screenwidth() - largura) // 2
        y = (self.root.winfo_screenheight() - altura) // 2
        self.root.geometry(f"{largura}x{altura}+{x}+{y}")
        self.root.minsize(700, 550)

        # Fontes
        self.font_titulo = tkfont.Font(family="Segoe UI", size=18, weight="bold")
        self.font_label = tkfont.Font(family="Segoe UI", size=11)
        self.font_btn = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        self.font_small = tkfont.Font(family="Segoe UI", size=9)
        self.font_mono = tkfont.Font(family="Consolas", size=10)
        self.font_card_num = tkfont.Font(family="Segoe UI", size=20, weight="bold")
        self.font_card_label = tkfont.Font(family="Segoe UI", size=9)

        # Estilo combobox
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.TCombobox",
            fieldbackground=CORES["input_bg"],
            background=CORES["accent"],
            foreground=CORES["text"],
            arrowcolor=CORES["text"],
            bordercolor=CORES["border"],
        )
        style.map("Dark.TCombobox",
            fieldbackground=[("readonly", CORES["input_bg"])],
            foreground=[("readonly", CORES["text"])],
        )

        # Estado
        self.resultados = []
        self.colunas_resultado = []

        self.construir_interface()

    # ──────────────────────────────────
    #  INTERFACE
    # ──────────────────────────────────
    def construir_interface(self):
        # ── TOPO ──
        topo = tk.Frame(self.root, bg=CORES["bg"], padx=24, pady=14)
        topo.pack(fill="x")

        tk.Label(
            topo, text="🕷  Web Scraper", font=self.font_titulo,
            bg=CORES["bg"], fg=CORES["text"]
        ).pack(side="left")

        # ── PAINEL DE CONTROLE ──
        painel = tk.Frame(self.root, bg=CORES["surface"], padx=20, pady=16)
        painel.pack(fill="x", padx=24, pady=(0, 8))

        # URL
        url_frame = tk.Frame(painel, bg=CORES["surface"])
        url_frame.pack(fill="x", pady=(0, 10))

        tk.Label(
            url_frame, text="URL:", font=self.font_label,
            bg=CORES["surface"], fg=CORES["muted"], width=12, anchor="w"
        ).pack(side="left")

        self.entry_url = tk.Entry(
            url_frame, font=self.font_mono,
            bg=CORES["input_bg"], fg=CORES["text"],
            insertbackground=CORES["text"],
            relief="flat", bd=0, highlightthickness=1,
            highlightcolor=CORES["accent"], highlightbackground=CORES["border"]
        )
        self.entry_url.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))
        self.entry_url.insert(0, "https://quotes.toscrape.com")

        # Tipo de extração
        tipo_frame = tk.Frame(painel, bg=CORES["surface"])
        tipo_frame.pack(fill="x", pady=(0, 10))

        tk.Label(
            tipo_frame, text="Extrair:", font=self.font_label,
            bg=CORES["surface"], fg=CORES["muted"], width=12, anchor="w"
        ).pack(side="left")

        self.var_tipo = tk.StringVar(value="Títulos (h1, h2, h3)")
        tipos = [
            "Títulos (h1, h2, h3)",
            "Links (URLs)",
            "Imagens (URLs)",
            "Tabelas",
            "Parágrafos (texto)",
            "Tudo (resumo geral)",
        ]
        combo_tipo = ttk.Combobox(
            tipo_frame, textvariable=self.var_tipo, values=tipos,
            state="readonly", style="Dark.TCombobox", font=self.font_label, width=30
        )
        combo_tipo.pack(side="left", padx=(0, 10))

        # Botões
        btn_frame = tk.Frame(painel, bg=CORES["surface"])
        btn_frame.pack(fill="x")

        self.btn_extrair = self.criar_botao(btn_frame, "🔍 Extrair Dados", self.iniciar_scraping, CORES["accent"])
        self.btn_extrair.pack(side="left", padx=(0, 8))

        self.btn_csv = self.criar_botao(btn_frame, "💾 Exportar CSV", self.exportar_csv, CORES["correct"])
        self.btn_csv.pack(side="left", padx=(0, 8))

        self.btn_limpar = self.criar_botao(btn_frame, "🗑 Limpar", self.limpar_resultados, CORES["wrong"])
        self.btn_limpar.pack(side="left")

        # Status
        self.label_status = tk.Label(
            painel, text="Pronto. Digite uma URL e clique em Extrair.",
            font=self.font_small, bg=CORES["surface"], fg=CORES["muted"], anchor="w"
        )
        self.label_status.pack(fill="x", pady=(10, 0))

        # ── CARDS RESUMO ──
        self.cards_frame = tk.Frame(self.root, bg=CORES["bg"], padx=24)
        self.cards_frame.pack(fill="x", pady=(4, 4))

        # ── ÁREA DE RESULTADOS ──
        resultado_frame = tk.Frame(self.root, bg=CORES["bg"])
        resultado_frame.pack(fill="both", expand=True, padx=24, pady=(0, 12))

        # Scrollbar
        scroll_y = tk.Scrollbar(resultado_frame, orient="vertical")
        scroll_y.pack(side="right", fill="y")

        scroll_x = tk.Scrollbar(resultado_frame, orient="horizontal")
        scroll_x.pack(side="bottom", fill="x")

        self.texto_resultado = tk.Text(
            resultado_frame, font=self.font_mono,
            bg=CORES["input_bg"], fg=CORES["text"],
            insertbackground=CORES["text"],
            relief="flat", bd=0, wrap="none",
            highlightthickness=1,
            highlightcolor=CORES["accent"],
            highlightbackground=CORES["border"],
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            padx=12, pady=12,
        )
        self.texto_resultado.pack(fill="both", expand=True)

        scroll_y.config(command=self.texto_resultado.yview)
        scroll_x.config(command=self.texto_resultado.xview)

        # Tags de cor
        self.texto_resultado.tag_configure("titulo", foreground=CORES["accent"], font=tkfont.Font(family="Consolas", size=10, weight="bold"))
        self.texto_resultado.tag_configure("destaque", foreground=CORES["accent2"])
        self.texto_resultado.tag_configure("numero", foreground=CORES["correct"])
        self.texto_resultado.tag_configure("erro", foreground=CORES["wrong"])

    # ──────────────────────────────────
    #  BOTÃO REUTILIZÁVEL
    # ──────────────────────────────────
    def criar_botao(self, parent, texto, comando, cor):
        btn = tk.Label(
            parent, text=texto, font=self.font_btn,
            bg=cor, fg="#fff" if cor != CORES["correct"] else "#000",
            padx=16, pady=8, cursor="hand2"
        )
        cor_hover = self.clarear_cor(cor)
        btn.bind("<Enter>", lambda e: btn.configure(bg=cor_hover))
        btn.bind("<Leave>", lambda e: btn.configure(bg=cor))
        btn.bind("<Button-1>", lambda e: comando())
        return btn

    def clarear_cor(self, hex_cor):
        r, g, b = int(hex_cor[1:3], 16), int(hex_cor[3:5], 16), int(hex_cor[5:7], 16)
        r = min(255, r + 30)
        g = min(255, g + 30)
        b = min(255, b + 30)
        return f"#{r:02x}{g:02x}{b:02x}"

    # ──────────────────────────────────
    #  SCRAPING
    # ──────────────────────────────────
    def iniciar_scraping(self):
        url = self.entry_url.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "Digite uma URL.")
            return
        if not url.startswith("http"):
            url = "https://" + url
            self.entry_url.delete(0, tk.END)
            self.entry_url.insert(0, url)

        self.label_status.configure(text="⏳ Carregando página...", fg=CORES["accent2"])
        self.root.update()

        # Roda em thread separada para não travar a interface
        thread = threading.Thread(target=self.executar_scraping, args=(url,))
        thread.start()

    def executar_scraping(self, url):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            resposta = requests.get(url, headers=headers, timeout=15)
            resposta.raise_for_status()

            soup = BeautifulSoup(resposta.text, "html.parser")
            tipo = self.var_tipo.get()

            if "Títulos" in tipo:
                self.extrair_titulos(soup, url)
            elif "Links" in tipo:
                self.extrair_links(soup, url)
            elif "Imagens" in tipo:
                self.extrair_imagens(soup, url)
            elif "Tabelas" in tipo:
                self.extrair_tabelas(soup, url)
            elif "Parágrafos" in tipo:
                self.extrair_paragrafos(soup, url)
            elif "Tudo" in tipo:
                self.extrair_tudo(soup, url)

        except requests.exceptions.ConnectionError:
            self.root.after(0, self.mostrar_erro, "Erro de conexão. Verifique a URL e sua internet.")
        except requests.exceptions.Timeout:
            self.root.after(0, self.mostrar_erro, "Tempo esgotado. O site demorou para responder.")
        except requests.exceptions.HTTPError as e:
            self.root.after(0, self.mostrar_erro, f"Erro HTTP: {e}")
        except Exception as e:
            self.root.after(0, self.mostrar_erro, f"Erro: {e}")

    def mostrar_erro(self, msg):
        self.label_status.configure(text=f"❌ {msg}", fg=CORES["wrong"])
        self.texto_resultado.delete("1.0", tk.END)
        self.texto_resultado.insert(tk.END, msg, "erro")

    # ──────────────────────────────────
    #  EXTRATORES
    # ──────────────────────────────────
    def extrair_titulos(self, soup, url):
        dados = []
        for tag in ["h1", "h2", "h3", "h4"]:
            for elem in soup.find_all(tag):
                texto = elem.get_text(strip=True)
                if texto:
                    dados.append({"tag": tag.upper(), "texto": texto})

        self.resultados = dados
        self.colunas_resultado = ["tag", "texto"]

        def atualizar():
            self.mostrar_cards({"Títulos": len(dados)})
            self.texto_resultado.delete("1.0", tk.END)
            if not dados:
                self.texto_resultado.insert(tk.END, "Nenhum título encontrado nesta página.", "erro")
            else:
                for i, item in enumerate(dados):
                    self.texto_resultado.insert(tk.END, f"[{item['tag']}] ", "numero")
                    self.texto_resultado.insert(tk.END, f"{item['texto']}\n\n")
            self.label_status.configure(text=f"✅ {len(dados)} títulos encontrados em {url}", fg=CORES["correct"])

        self.root.after(0, atualizar)

    def extrair_links(self, soup, url):
        dados = []
        for a in soup.find_all("a", href=True):
            texto = a.get_text(strip=True) or "(sem texto)"
            href = a["href"]
            if href.startswith("/"):
                from urllib.parse import urljoin
                href = urljoin(url, href)
            dados.append({"texto": texto, "url": href})

        self.resultados = dados
        self.colunas_resultado = ["texto", "url"]

        def atualizar():
            internos = sum(1 for d in dados if url.split("/")[2] in d["url"])
            externos = len(dados) - internos
            self.mostrar_cards({"Total Links": len(dados), "Internos": internos, "Externos": externos})
            self.texto_resultado.delete("1.0", tk.END)
            if not dados:
                self.texto_resultado.insert(tk.END, "Nenhum link encontrado.", "erro")
            else:
                for i, item in enumerate(dados):
                    self.texto_resultado.insert(tk.END, f"{i+1}. ", "numero")
                    self.texto_resultado.insert(tk.END, f"{item['texto']}\n", "titulo")
                    self.texto_resultado.insert(tk.END, f"   {item['url']}\n\n", "destaque")
            self.label_status.configure(text=f"✅ {len(dados)} links encontrados em {url}", fg=CORES["correct"])

        self.root.after(0, atualizar)

    def extrair_imagens(self, soup, url):
        from urllib.parse import urljoin
        dados = []
        for img in soup.find_all("img"):
            src = img.get("src", "")
            alt = img.get("alt", "(sem descrição)")
            if src:
                if src.startswith("/"):
                    src = urljoin(url, src)
                dados.append({"descricao": alt, "url": src})

        self.resultados = dados
        self.colunas_resultado = ["descricao", "url"]

        def atualizar():
            self.mostrar_cards({"Imagens": len(dados)})
            self.texto_resultado.delete("1.0", tk.END)
            if not dados:
                self.texto_resultado.insert(tk.END, "Nenhuma imagem encontrada.", "erro")
            else:
                for i, item in enumerate(dados):
                    self.texto_resultado.insert(tk.END, f"{i+1}. ", "numero")
                    self.texto_resultado.insert(tk.END, f"{item['descricao']}\n")
                    self.texto_resultado.insert(tk.END, f"   {item['url']}\n\n", "destaque")
            self.label_status.configure(text=f"✅ {len(dados)} imagens encontradas em {url}", fg=CORES["correct"])

        self.root.after(0, atualizar)

    def extrair_tabelas(self, soup, url):
        tabelas = soup.find_all("table")
        todos_dados = []
        texto_saida = []

        for t_idx, tabela in enumerate(tabelas):
            linhas = tabela.find_all("tr")
            texto_saida.append(f"═══ Tabela {t_idx + 1} ({len(linhas)} linhas) ═══\n\n")

            for linha in linhas:
                celulas = linha.find_all(["th", "td"])
                valores = [c.get_text(strip=True) for c in celulas]
                todos_dados.append({"tabela": t_idx + 1, "dados": " | ".join(valores)})
                texto_saida.append(" | ".join(valores) + "\n")
            texto_saida.append("\n")

        self.resultados = todos_dados
        self.colunas_resultado = ["tabela", "dados"]

        def atualizar():
            self.mostrar_cards({"Tabelas": len(tabelas), "Linhas totais": len(todos_dados)})
            self.texto_resultado.delete("1.0", tk.END)
            if not tabelas:
                self.texto_resultado.insert(tk.END, "Nenhuma tabela encontrada nesta página.", "erro")
            else:
                for parte in texto_saida:
                    if parte.startswith("═══"):
                        self.texto_resultado.insert(tk.END, parte, "titulo")
                    else:
                        self.texto_resultado.insert(tk.END, parte)
            self.label_status.configure(text=f"✅ {len(tabelas)} tabelas encontradas em {url}", fg=CORES["correct"])

        self.root.after(0, atualizar)

    def extrair_paragrafos(self, soup, url):
        dados = []
        for p in soup.find_all("p"):
            texto = p.get_text(strip=True)
            if texto and len(texto) > 10:
                dados.append({"texto": texto})

        self.resultados = dados
        self.colunas_resultado = ["texto"]

        def atualizar():
            total_palavras = sum(len(d["texto"].split()) for d in dados)
            self.mostrar_cards({"Parágrafos": len(dados), "Palavras": total_palavras})
            self.texto_resultado.delete("1.0", tk.END)
            if not dados:
                self.texto_resultado.insert(tk.END, "Nenhum parágrafo encontrado.", "erro")
            else:
                for i, item in enumerate(dados):
                    self.texto_resultado.insert(tk.END, f"[{i+1}] ", "numero")
                    self.texto_resultado.insert(tk.END, f"{item['texto']}\n\n")
            self.label_status.configure(text=f"✅ {len(dados)} parágrafos encontrados em {url}", fg=CORES["correct"])

        self.root.after(0, atualizar)

    def extrair_tudo(self, soup, url):
        titulo = soup.title.string.strip() if soup.title and soup.title.string else "(sem título)"
        h1s = len(soup.find_all("h1"))
        h2s = len(soup.find_all("h2"))
        h3s = len(soup.find_all("h3"))
        links = len(soup.find_all("a", href=True))
        imgs = len(soup.find_all("img"))
        tabelas = len(soup.find_all("table"))
        paragrafos = soup.find_all("p")
        ps = len(paragrafos)
        palavras = sum(len(p.get_text(strip=True).split()) for p in paragrafos)
        forms = len(soup.find_all("form"))
        scripts = len(soup.find_all("script"))
        metas = len(soup.find_all("meta"))

        resumo = [
            ("Título da Página", titulo),
            ("", ""),
            ("── ESTRUTURA ──", ""),
            ("H1", str(h1s)),
            ("H2", str(h2s)),
            ("H3", str(h3s)),
            ("Parágrafos", str(ps)),
            ("Total de Palavras", str(palavras)),
            ("", ""),
            ("── RECURSOS ──", ""),
            ("Links", str(links)),
            ("Imagens", str(imgs)),
            ("Tabelas", str(tabelas)),
            ("Formulários", str(forms)),
            ("", ""),
            ("── TÉCNICO ──", ""),
            ("Scripts", str(scripts)),
            ("Meta Tags", str(metas)),
        ]

        self.resultados = [{"item": r[0], "valor": r[1]} for r in resumo if r[0]]
        self.colunas_resultado = ["item", "valor"]

        def atualizar():
            self.mostrar_cards({"Links": links, "Imagens": imgs, "Parágrafos": ps, "Palavras": palavras})
            self.texto_resultado.delete("1.0", tk.END)
            for item, valor in resumo:
                if item.startswith("──"):
                    self.texto_resultado.insert(tk.END, f"\n{item}\n", "titulo")
                elif item:
                    self.texto_resultado.insert(tk.END, f"  {item}: ", "destaque")
                    self.texto_resultado.insert(tk.END, f"{valor}\n")
                else:
                    self.texto_resultado.insert(tk.END, "\n")
            self.label_status.configure(text=f"✅ Resumo completo de {url}", fg=CORES["correct"])

        self.root.after(0, atualizar)

    # ──────────────────────────────────
    #  CARDS
    # ──────────────────────────────────
    def mostrar_cards(self, info):
        for w in self.cards_frame.winfo_children():
            w.destroy()

        cores = [CORES["accent"], CORES["accent2"], CORES["accent3"], CORES["correct"]]
        items = list(info.items())[:4]

        for i in range(len(items)):
            self.cards_frame.columnconfigure(i, weight=1, uniform="card")

        for i, (label, valor) in enumerate(items):
            cor = cores[i % len(cores)]
            card = tk.Frame(self.cards_frame, bg=CORES["surface"], padx=16, pady=10)
            card.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)

            barra = tk.Frame(card, bg=cor, width=4, height=30)
            barra.pack(side="left", padx=(0, 10))

            info_frame = tk.Frame(card, bg=CORES["surface"])
            info_frame.pack(side="left", fill="x", expand=True)

            tk.Label(info_frame, text=label.upper(), font=self.font_card_label,
                     bg=CORES["surface"], fg=CORES["muted"], anchor="w").pack(fill="x")
            tk.Label(info_frame, text=str(valor), font=self.font_card_num,
                     bg=CORES["surface"], fg=cor, anchor="w").pack(fill="x")

    # ──────────────────────────────────
    #  EXPORTAR CSV
    # ──────────────────────────────────
    def exportar_csv(self):
        if not self.resultados:
            messagebox.showwarning("Aviso", "Nenhum dado para exportar. Extraia dados primeiro.")
            return

        caminho = filedialog.asksaveasfilename(
            title="Salvar CSV",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Todos", "*.*")],
            initialfile="dados_extraidos.csv"
        )
        if caminho:
            try:
                with open(caminho, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=self.colunas_resultado)
                    writer.writeheader()
                    writer.writerows(self.resultados)
                self.label_status.configure(
                    text=f"💾 Exportado com sucesso: {os.path.basename(caminho)}",
                    fg=CORES["correct"]
                )
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar:\n{e}")

    # ──────────────────────────────────
    #  LIMPAR
    # ──────────────────────────────────
    def limpar_resultados(self):
        self.texto_resultado.delete("1.0", tk.END)
        self.resultados = []
        self.colunas_resultado = []
        for w in self.cards_frame.winfo_children():
            w.destroy()
        self.label_status.configure(text="Pronto. Digite uma URL e clique em Extrair.", fg=CORES["muted"])


# ════════════════════════════════════════
#  INICIAR
# ════════════════════════════════════════

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = ScraperApp(root)
        root.mainloop()
    except Exception as e:
        import traceback
        erro = traceback.format_exc()
        try:
            r = tk.Tk()
            r.withdraw()
            messagebox.showerror("Erro ao iniciar", f"Ocorreu um erro:\n\n{erro}")
            r.destroy()
        except:
            print(erro)
            input("Pressione Enter para fechar...")
