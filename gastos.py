import json
import math
import os
from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox

ARQUIVO = "gastos.json"
ARQUIVO_CONFIG = "config.json"

CATEGORIAS = ["comida", "transporte", "lazer", "moradia", "saude", "estudos", "outros"]

# cores usadas na janela toda, ficam aqui pra trocar num lugar so
COR_FUNDO = "#eef1f5"
COR_CARTAO = "#ffffff"
COR_TOPO = "#1f3a5f"
COR_DESTAQUE = "#2f6fdb"
COR_OK = "#2e7d32"
COR_ALERTA = "#c62828"


def ler_json(caminho, padrao):
    if not os.path.exists(caminho):
        return padrao
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # arquivo estragado: guarda uma copia e comeca de novo em vez de travar
        os.replace(caminho, caminho + ".bak")
        return padrao


def gravar_json(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)


def carregar():
    return ler_json(ARQUIVO, [])


def salvar(gastos):
    gravar_json(ARQUIVO, gastos)


def carregar_limite():
    return ler_json(ARQUIVO_CONFIG, {}).get("limite_mensal", 0)


def salvar_limite(limite):
    gravar_json(ARQUIVO_CONFIG, {"limite_mensal": limite})


def total_do_mes(gastos, mes_ano):
    # a data fica salva como dd/mm/aaaa, entao os 7 ultimos caracteres sao o mm/aaaa
    return sum(g["valor"] for g in gastos if g["data"][3:] == mes_ano)


def ler_valor(texto, aceita_zero=False):
    # aceita 25,50 ou 25.50; devolve None se nao for um numero valido
    try:
        valor = float(texto.strip().replace(",", "."))
    except ValueError:
        return None
    if not math.isfinite(valor) or valor < 0 or (valor == 0 and not aceita_zero):
        return None
    return valor


class App:
    def __init__(self, janela):
        self.janela = janela
        self.janela.title("Controle de Gastos")
        self.janela.geometry("720x620")
        self.janela.resizable(False, False)
        self.janela.configure(bg=COR_FUNDO)

        self.aplicar_estilo()

        self.gastos = carregar()
        self.limite = carregar_limite()

        self.montar_topo()
        self.montar_formulario()
        self.montar_limite()
        self.montar_filtro()
        # o rodape vem antes da tabela pra ficar preso embaixo e a tabela ocupar o que sobrar
        self.montar_rodape()
        self.montar_tabela()
        self.atualizar_tabela()

    def aplicar_estilo(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(".", background=COR_FUNDO, font=("Segoe UI", 10))
        estilo.configure("Cartao.TLabelframe", background=COR_CARTAO, bordercolor="#d5dbe3")
        estilo.configure("Cartao.TLabelframe.Label", background=COR_CARTAO,
                         foreground=COR_TOPO, font=("Segoe UI", 10, "bold"))
        estilo.configure("Cartao.TLabel", background=COR_CARTAO)
        estilo.configure("TButton", padding=(10, 5))
        estilo.configure("Destaque.TButton", background=COR_DESTAQUE, foreground="white",
                         font=("Segoe UI", 10, "bold"), borderwidth=0)
        estilo.map("Destaque.TButton", background=[("active", "#2559b3")])
        estilo.configure("Treeview", rowheight=28, background="white", fieldbackground="white")
        estilo.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                         background=COR_TOPO, foreground="white", padding=5)
        estilo.map("Treeview.Heading", background=[("active", COR_TOPO)])
        estilo.map("Treeview", background=[("selected", COR_DESTAQUE)])
        estilo.configure("Ok.Horizontal.TProgressbar", background=COR_OK, troughcolor="#e3e7ec")
        estilo.configure("Alerta.Horizontal.TProgressbar", background=COR_ALERTA, troughcolor="#e3e7ec")

    # ---------- faixa azul com o titulo ----------
    def montar_topo(self):
        topo = tk.Frame(self.janela, bg=COR_TOPO, height=56)
        topo.pack(fill="x")
        topo.pack_propagate(False)

        tk.Label(topo, text="Controle de Gastos", bg=COR_TOPO, fg="white",
                 font=("Segoe UI", 16, "bold")).pack(side="left", padx=15)
        tk.Label(topo, text=f"Hoje: {date.today().strftime('%d/%m/%Y')}", bg=COR_TOPO,
                 fg="#c9d6ea", font=("Segoe UI", 10)).pack(side="right", padx=15)

    # ---------- formulario ----------
    def montar_formulario(self):
        frame = ttk.LabelFrame(self.janela, text="Novo gasto", padding=10, style="Cartao.TLabelframe")
        frame.pack(fill="x", padx=12, pady=(12, 6))

        ttk.Label(frame, text="Descrição:", style="Cartao.TLabel").grid(row=0, column=0, sticky="w")
        self.ent_descricao = ttk.Entry(frame, width=32)
        self.ent_descricao.grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Valor (R$):", style="Cartao.TLabel").grid(row=0, column=2, sticky="w")
        self.ent_valor = ttk.Entry(frame, width=12)
        self.ent_valor.grid(row=0, column=3, padx=5)

        ttk.Label(frame, text="Categoria:", style="Cartao.TLabel").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.cb_categoria = ttk.Combobox(frame, values=CATEGORIAS, width=29, state="readonly")
        self.cb_categoria.current(0)
        self.cb_categoria.grid(row=1, column=1, padx=5, pady=(8, 0))

        btn = ttk.Button(frame, text="Adicionar", style="Destaque.TButton", command=self.adicionar)
        btn.grid(row=1, column=3, padx=5, pady=(8, 0), sticky="e")

        # enter no campo de valor tambem adiciona
        self.ent_valor.bind("<Return>", lambda e: self.adicionar())

    # ---------- limite do mes ----------
    def montar_limite(self):
        frame = ttk.LabelFrame(self.janela, text="Limite do mês", padding=10, style="Cartao.TLabelframe")
        frame.pack(fill="x", padx=12, pady=6)

        self.lbl_limite = ttk.Label(frame, style="Cartao.TLabel")
        self.lbl_limite.grid(row=0, column=0, sticky="w")

        ttk.Button(frame, text="Definir limite", command=self.definir_limite).grid(row=0, column=1, sticky="e")
        frame.columnconfigure(0, weight=1)

        self.barra = ttk.Progressbar(frame, maximum=100, style="Ok.Horizontal.TProgressbar")
        self.barra.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))

    # ---------- filtro por categoria ----------
    def montar_filtro(self):
        frame = ttk.Frame(self.janela)
        frame.pack(fill="x", padx=12, pady=(6, 0))

        ttk.Label(frame, text="Mostrar:").pack(side="left")
        self.cb_filtro = ttk.Combobox(frame, values=["todas"] + CATEGORIAS, width=15, state="readonly")
        self.cb_filtro.current(0)
        self.cb_filtro.pack(side="left", padx=5)
        self.cb_filtro.bind("<<ComboboxSelected>>", lambda e: self.atualizar_tabela())

    # ---------- tabela ----------
    def montar_tabela(self):
        frame = ttk.Frame(self.janela)
        frame.pack(fill="both", expand=True, padx=12, pady=6)

        colunas = ("data", "categoria", "descricao", "valor")
        self.tabela = ttk.Treeview(frame, columns=colunas, show="headings", height=8)
        self.tabela.heading("data", text="Data")
        self.tabela.heading("categoria", text="Categoria")
        self.tabela.heading("descricao", text="Descrição")
        self.tabela.heading("valor", text="Valor (R$)")

        self.tabela.column("data", width=95, anchor="center")
        self.tabela.column("categoria", width=110, anchor="center")
        self.tabela.column("descricao", width=300)
        self.tabela.column("valor", width=110, anchor="e")

        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=scroll.set)

        self.tabela.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.tabela.bind("<Delete>", lambda e: self.remover())

        # linhas alternadas pra facilitar a leitura
        self.tabela.tag_configure("par", background="#f5f8fc")

    # ---------- rodape: total e botoes ----------
    def montar_rodape(self):
        frame = ttk.Frame(self.janela)
        frame.pack(side="bottom", fill="x", padx=12, pady=(6, 12))

        self.lbl_total = ttk.Label(frame, text="Total: R$ 0,00", font=("Segoe UI", 12, "bold"), foreground=COR_OK)
        self.lbl_total.pack(side="left")

        ttk.Button(frame, text="Remover selecionado", command=self.remover).pack(side="right", padx=(5, 0))
        ttk.Button(frame, text="Resumo por categoria", command=self.mostrar_resumo).pack(side="right")

    # ---------- acoes ----------
    def adicionar(self):
        descricao = self.ent_descricao.get().strip()
        categoria = self.cb_categoria.get()

        if descricao == "":
            messagebox.showwarning("Atenção", "Digite uma descrição.")
            return

        valor = ler_valor(self.ent_valor.get())
        if valor is None:
            messagebox.showwarning("Atenção", "Valor inválido. Use um número maior que zero, ex: 25,50")
            return

        mes_ano = date.today().strftime("%m/%Y")
        estava_no_limite = self.dentro_do_limite(mes_ano)

        self.gastos.append({
            "descricao": descricao,
            "valor": valor,
            "categoria": categoria,
            "data": date.today().strftime("%d/%m/%Y")
        })
        salvar(self.gastos)
        self.atualizar_tabela()

        # avisa so na hora que passa do limite, pra nao ficar avisando a cada gasto
        if estava_no_limite and not self.dentro_do_limite(mes_ano):
            messagebox.showwarning("Limite do mês", "Você passou do limite de gastos deste mês!")

        # limpa os campos pra digitar o proximo
        self.ent_descricao.delete(0, "end")
        self.ent_valor.delete(0, "end")
        self.ent_descricao.focus()

    def dentro_do_limite(self, mes_ano):
        return self.limite == 0 or total_do_mes(self.gastos, mes_ano) <= self.limite

    def definir_limite(self):
        popup = tk.Toplevel(self.janela)
        popup.title("Limite do mês")
        popup.geometry("300x130")
        popup.resizable(False, False)
        popup.configure(bg=COR_FUNDO)
        popup.transient(self.janela)
        popup.grab_set()

        ttk.Label(popup, text="Quanto quer gastar no máximo por mês? (0 = sem limite)").pack(padx=10, pady=(12, 6))
        ent = ttk.Entry(popup, width=15, justify="center")
        ent.insert(0, formatar(self.limite))
        ent.pack()
        ent.focus()
        ent.select_range(0, "end")

        def confirmar():
            # aqui zero vale, porque significa "tirar o limite"
            valor = ler_valor(ent.get(), aceita_zero=True)
            if valor is None:
                messagebox.showwarning("Atenção", "Valor inválido.", parent=popup)
                return
            self.limite = valor
            salvar_limite(valor)
            self.atualizar_limite()
            popup.destroy()

        ttk.Button(popup, text="Salvar", style="Destaque.TButton", command=confirmar).pack(pady=10)
        ent.bind("<Return>", lambda e: confirmar())

    def atualizar_limite(self):
        gasto = total_do_mes(self.gastos, date.today().strftime("%m/%Y"))

        if self.limite == 0:
            self.lbl_limite.config(text=f"Gasto neste mês: R$ {formatar(gasto)}  (sem limite definido)",
                                   foreground="black")
            self.barra.config(value=0, style="Ok.Horizontal.TProgressbar")
            return

        pct = gasto / self.limite * 100
        passou = gasto > self.limite
        self.lbl_limite.config(
            text=f"Gasto neste mês: R$ {formatar(gasto)} de R$ {formatar(self.limite)}  ({pct:.0f}%)",
            foreground=COR_ALERTA if passou else "black")
        self.barra.config(value=min(pct, 100),
                          style="Alerta.Horizontal.TProgressbar" if passou else "Ok.Horizontal.TProgressbar")

    def remover(self):
        selecionado = self.tabela.selection()
        if not selecionado:
            messagebox.showinfo("Remover", "Selecione um gasto na lista primeiro.")
            return

        # o iid da linha é o indice na lista de gastos
        indice = int(selecionado[0])
        g = self.gastos[indice]

        if messagebox.askyesno("Remover", f"Remover '{g['descricao']}' (R$ {formatar(g['valor'])})?"):
            self.gastos.pop(indice)
            salvar(self.gastos)
            self.atualizar_tabela()

    def atualizar_tabela(self):
        for linha in self.tabela.get_children():
            self.tabela.delete(linha)

        filtro = self.cb_filtro.get()

        total = 0
        linha = 0
        for i, g in enumerate(self.gastos):
            if filtro != "todas" and g["categoria"] != filtro:
                continue
            # o iid continua sendo o indice na lista completa, entao remover funciona com filtro
            self.tabela.insert("", "end", iid=str(i), tags=("par",) if linha % 2 else (), values=(
                g["data"],
                g["categoria"],
                g["descricao"],
                formatar(g["valor"])
            ))
            total += g["valor"]
            linha += 1

        self.lbl_total.config(text=f"Total: R$ {formatar(total)}")
        self.atualizar_limite()

    def mostrar_resumo(self):
        if len(self.gastos) == 0:
            messagebox.showinfo("Resumo", "Nenhum gasto cadastrado ainda.")
            return

        totais = {}
        for g in self.gastos:
            totais[g["categoria"]] = totais.get(g["categoria"], 0) + g["valor"]
        total_geral = sum(totais.values())

        popup = tk.Toplevel(self.janela)
        popup.title("Resumo por categoria")
        popup.geometry("400x300")
        popup.resizable(False, False)
        popup.configure(bg=COR_FUNDO)

        colunas = ("categoria", "valor", "pct")
        tabela = ttk.Treeview(popup, columns=colunas, show="headings")
        tabela.heading("categoria", text="Categoria")
        tabela.heading("valor", text="Total (R$)")
        tabela.heading("pct", text="%")
        tabela.column("categoria", width=150)
        tabela.column("valor", width=120, anchor="e")
        tabela.column("pct", width=80, anchor="e")
        tabela.pack(fill="both", expand=True, padx=10, pady=10)

        # da categoria que mais gastou pra que menos gastou
        for cat, valor in sorted(totais.items(), key=lambda x: x[1], reverse=True):
            pct = valor / total_geral * 100
            tabela.insert("", "end", values=(cat, formatar(valor), f"{pct:.1f}%"))

        ttk.Label(popup, text=f"Total geral: R$ {formatar(total_geral)}",
                  font=("Segoe UI", 10, "bold")).pack(pady=(0, 10))


def formatar(valor):
    # troca o ponto por virgula pra ficar no formato brasileiro
    return f"{valor:.2f}".replace(".", ",")


if __name__ == "__main__":
    janela = tk.Tk()
    App(janela)
    janela.mainloop()
