import json
import os
from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox

ARQUIVO = "gastos.json"

CATEGORIAS = ["comida", "transporte", "lazer", "moradia", "saude", "estudos", "outros"]


def carregar():
    if not os.path.exists(ARQUIVO):
        return []
    with open(ARQUIVO, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar(gastos):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(gastos, f, indent=2, ensure_ascii=False)


class App:
    def __init__(self, janela):
        self.janela = janela
        self.janela.title("Controle de Gastos")
        self.janela.geometry("640x480")
        self.janela.resizable(False, False)

        self.gastos = carregar()

        self.montar_formulario()
        self.montar_tabela()
        self.montar_rodape()
        self.atualizar_tabela()

    # ---------- parte de cima: formulario ----------
    def montar_formulario(self):
        frame = ttk.LabelFrame(self.janela, text="Novo gasto", padding=10)
        frame.pack(fill="x", padx=10, pady=(10, 5))

        ttk.Label(frame, text="Descrição:").grid(row=0, column=0, sticky="w")
        self.ent_descricao = ttk.Entry(frame, width=30)
        self.ent_descricao.grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Valor (R$):").grid(row=0, column=2, sticky="w")
        self.ent_valor = ttk.Entry(frame, width=10)
        self.ent_valor.grid(row=0, column=3, padx=5)

        ttk.Label(frame, text="Categoria:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.cb_categoria = ttk.Combobox(frame, values=CATEGORIAS, width=27, state="readonly")
        self.cb_categoria.current(0)
        self.cb_categoria.grid(row=1, column=1, padx=5, pady=(8, 0))

        btn = ttk.Button(frame, text="Adicionar", command=self.adicionar)
        btn.grid(row=1, column=3, padx=5, pady=(8, 0), sticky="e")

        # enter no campo de valor tambem adiciona
        self.ent_valor.bind("<Return>", lambda e: self.adicionar())

    # ---------- meio: tabela ----------
    def montar_tabela(self):
        frame = ttk.Frame(self.janela)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        colunas = ("data", "categoria", "descricao", "valor")
        self.tabela = ttk.Treeview(frame, columns=colunas, show="headings", height=10)
        self.tabela.heading("data", text="Data")
        self.tabela.heading("categoria", text="Categoria")
        self.tabela.heading("descricao", text="Descrição")
        self.tabela.heading("valor", text="Valor (R$)")

        self.tabela.column("data", width=90, anchor="center")
        self.tabela.column("categoria", width=100, anchor="center")
        self.tabela.column("descricao", width=280)
        self.tabela.column("valor", width=100, anchor="e")

        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=scroll.set)

        self.tabela.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    # ---------- parte de baixo: total e botoes ----------
    def montar_rodape(self):
        frame = ttk.Frame(self.janela)
        frame.pack(fill="x", padx=10, pady=(5, 10))

        self.lbl_total = ttk.Label(frame, text="Total: R$ 0,00", font=("Segoe UI", 11, "bold"))
        self.lbl_total.pack(side="left")

        ttk.Button(frame, text="Remover selecionado", command=self.remover).pack(side="right", padx=(5, 0))
        ttk.Button(frame, text="Resumo por categoria", command=self.mostrar_resumo).pack(side="right")

    # ---------- acoes ----------
    def adicionar(self):
        descricao = self.ent_descricao.get().strip()
        valor_txt = self.ent_valor.get().strip().replace(",", ".")
        categoria = self.cb_categoria.get()

        if descricao == "":
            messagebox.showwarning("Atenção", "Digite uma descrição.")
            return

        try:
            valor = float(valor_txt)
        except ValueError:
            messagebox.showwarning("Atenção", "Valor inválido. Use números, ex: 25,50")
            return

        if valor <= 0:
            messagebox.showwarning("Atenção", "O valor tem que ser maior que zero.")
            return

        self.gastos.append({
            "descricao": descricao,
            "valor": valor,
            "categoria": categoria,
            "data": date.today().strftime("%d/%m/%Y")
        })
        salvar(self.gastos)
        self.atualizar_tabela()

        # limpa os campos pra digitar o proximo
        self.ent_descricao.delete(0, "end")
        self.ent_valor.delete(0, "end")
        self.ent_descricao.focus()

    def remover(self):
        selecionado = self.tabela.selection()
        if not selecionado:
            messagebox.showinfo("Remover", "Selecione um gasto na lista primeiro.")
            return

        # o iid da linha é o indice na lista de gastos
        indice = int(selecionado[0])
        g = self.gastos[indice]

        if messagebox.askyesno("Remover", f"Remover '{g['descricao']}' (R$ {g['valor']:.2f})?"):
            self.gastos.pop(indice)
            salvar(self.gastos)
            self.atualizar_tabela()

    def atualizar_tabela(self):
        for linha in self.tabela.get_children():
            self.tabela.delete(linha)

        total = 0
        for i, g in enumerate(self.gastos):
            self.tabela.insert("", "end", iid=str(i), values=(
                g["data"],
                g["categoria"],
                g["descricao"],
                formatar(g["valor"])
            ))
            total += g["valor"]

        self.lbl_total.config(text=f"Total: R$ {formatar(total)}")

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
