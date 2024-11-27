import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox

class Produto:
    def __init__(self, codigo, descricao, quantidade, preco):
        self.codigo = codigo
        self.descricao = descricao
        self.quantidade = quantidade
        self.preco = preco

class Estoque:
    def __init__(self, produtos):
        self.produtos = pd.DataFrame([vars(p) for p in produtos])

    def mostrar_estoque(self):
        return self.produtos

    def atualizar_estoque(self, codigo, quantidade):
        condicao = self.produtos['codigo'] == codigo
        if not self.produtos[condicao].empty:
            self.produtos.loc[condicao, 'quantidade'] += quantidade
            return "Estoque atualizado com sucesso."
        else:
            return "Código do produto não encontrado."

    def verificar_disponibilidade(self, codigo, quantidade):
        condicao = self.produtos['codigo'] == codigo
        item = self.produtos[condicao]
        if not item.empty and item['quantidade'].values[0] >= quantidade:
            return True, item
        return False, None

    def baixar_estoque(self, codigo, quantidade):
        condicao = self.produtos['codigo'] == codigo
        self.produtos.loc[condicao, 'quantidade'] -= quantidade

class Cliente:
    def __init__(self, nome):
        self.nome = nome
        self.compras = []
        self.valor_total = 0.0

    def registrar_compra(self, produto, quantidade):
        total_item = quantidade * produto.preco
        self.compras.append({
            "Código": produto.codigo,
            "Descrição": produto.descricao,
            "Preço": produto.preco,
            "Quantidade": quantidade,
            "Total": total_item
        })
        self.valor_total += total_item

    def mostrar_compras(self):
        return pd.DataFrame(self.compras) if self.compras else None

class SistemaVendasApp:
    def __init__(self, root, estoque):
        self.estoque = estoque
        self.clientes = {}

        # Configuração da janela principal
        self.root = root
        self.root.title("Sistema de Vendas")
        self.root.geometry("600x600")
        self.root.config(bg="#e0f7fa")  # Cor de fundo verde água suave

        # Seções da interface
        self.create_main_menu()
        self.create_estoque_table()
        self.create_navigation_buttons()
        self.create_venda_section()
        self.create_reposicao_section()
        self.create_vendas_realizadas_section()

        # Ocultar seções inicialmente
        self.venda_frame.pack_forget()
        self.reposicao_frame.pack_forget()
        self.vendas_realizadas_frame.pack_forget()

    def create_main_menu(self):
        menu_frame = tk.Frame(self.root, bg="#e0f7fa")
        menu_frame.pack(pady=10)

        tk.Label(menu_frame, text="Sistema de Vendas e Estoque", font=("Arial", 16), bg="#e0f7fa", fg="#00796b").pack()

    def create_estoque_table(self):
        self.table_frame = tk.Frame(self.root, bg="#e0f7fa")
        self.table_frame.pack(pady=10)

        self.table = ttk.Treeview(self.table_frame, columns=("Código", "Descrição", "Quantidade", "Preço"), show="headings")
        for col in self.table["columns"]:
            self.table.heading(col, text=col)
            self.table.column(col, width=100)
        self.table.pack()

        self.update_estoque_table()

    def update_estoque_table(self):
        for i in self.table.get_children():
            self.table.delete(i)
        for _, row in self.estoque.mostrar_estoque().iterrows():
            self.table.insert("", "end", values=(row['codigo'], row['descricao'], row['quantidade'], row['preco']))

    def create_navigation_buttons(self):
        nav_frame = tk.Frame(self.root, bg="#e0f7fa")
        nav_frame.pack(pady=20)

        tk.Button(nav_frame, text="Abrir Registro de Venda", command=self.show_venda_section, bg="#00796b", fg="white", relief="flat").pack(side=tk.LEFT, padx=10)
        tk.Button(nav_frame, text="Abrir Reposição de Estoque", command=self.show_reposicao_section, bg="#00796b", fg="white", relief="flat").pack(side=tk.LEFT, padx=10)
        tk.Button(nav_frame, text="Ver Vendas Realizadas", command=self.show_vendas_realizadas_section, bg="#00796b", fg="white", relief="flat").pack(side=tk.LEFT, padx=10)

    def create_venda_section(self):
        self.venda_frame = tk.Frame(self.root, bg="#e0f7fa")
        
        tk.Label(self.venda_frame, text="Registro de Venda", font=("Arial", 14), bg="#e0f7fa", fg="#00796b").pack()

        tk.Label(self.venda_frame, text="Nome do Cliente:", bg="#e0f7fa", fg="#00796b").pack()
        self.nome_cliente_entry = tk.Entry(self.venda_frame)
        self.nome_cliente_entry.pack()

        tk.Label(self.venda_frame, text="Código do Produto:", bg="#e0f7fa", fg="#00796b").pack()
        self.codigo_produto_entry = tk.Entry(self.venda_frame)
        self.codigo_produto_entry.pack()

        tk.Label(self.venda_frame, text="Quantidade:", bg="#e0f7fa", fg="#00796b").pack()
        self.quantidade_entry = tk.Entry(self.venda_frame)
        self.quantidade_entry.pack()

        tk.Button(self.venda_frame, text="Registrar Venda", command=self.registrar_venda, bg="#00796b", fg="white", relief="flat").pack(pady=5)

    def registrar_venda(self):
        nome_cliente = self.nome_cliente_entry.get()
        codigo_produto = int(self.codigo_produto_entry.get())
        quantidade = int(self.quantidade_entry.get())

        if nome_cliente not in self.clientes:
            self.clientes[nome_cliente] = Cliente(nome_cliente)

        cliente = self.clientes[nome_cliente]
        disponivel, item = self.estoque.verificar_disponibilidade(codigo_produto, quantidade)

        if disponivel:
            produto = Produto(
                codigo=item['codigo'].values[0],
                descricao=item['descricao'].values[0],
                quantidade=item['quantidade'].values[0],
                preco=item['preco'].values[0]
            )
            cliente.registrar_compra(produto, quantidade)
            self.estoque.baixar_estoque(codigo_produto, quantidade)
            self.update_estoque_table()
            self.update_vendas_table()  # Atualiza a tabela de vendas após cada venda
            messagebox.showinfo("Sucesso", f"Venda de {quantidade}x {produto.descricao} registrada para {nome_cliente}.")
        else:
            messagebox.showerror("Erro", "Quantidade solicitada não disponível em estoque.")

    def create_reposicao_section(self):
        self.reposicao_frame = tk.Frame(self.root, bg="#e0f7fa")

        tk.Label(self.reposicao_frame, text="Repor Estoque", font=("Arial", 14), bg="#e0f7fa", fg="#00796b").pack()

        tk.Label(self.reposicao_frame, text="Código do Produto:", bg="#e0f7fa", fg="#00796b").pack()
        self.repor_codigo_entry = tk.Entry(self.reposicao_frame)
        self.repor_codigo_entry.pack()

        tk.Label(self.reposicao_frame, text="Quantidade a Adicionar:", bg="#e0f7fa", fg="#00796b").pack()
        self.repor_quantidade_entry = tk.Entry(self.reposicao_frame)
        self.repor_quantidade_entry.pack()

        tk.Button(self.reposicao_frame, text="Repor Estoque", command=self.repor_estoque, bg="#00796b", fg="white", relief="flat").pack(pady=5)

    def repor_estoque(self):
        codigo = int(self.repor_codigo_entry.get())
        quantidade = int(self.repor_quantidade_entry.get())
        mensagem = self.estoque.atualizar_estoque(codigo, quantidade)
        self.update_estoque_table()
        messagebox.showinfo("Resultado", mensagem)

    def show_venda_section(self):
        self.reposicao_frame.pack_forget()
        self.vendas_realizadas_frame.pack_forget()
        self.venda_frame.pack(pady=10)

    def show_reposicao_section(self):
        self.venda_frame.pack_forget()
        self.vendas_realizadas_frame.pack_forget()
        self.reposicao_frame.pack(pady=10)

    def show_vendas_realizadas_section(self):
        self.venda_frame.pack_forget()
        self.reposicao_frame.pack_forget()
        self.vendas_realizadas_frame.pack(pady=10)

    def create_vendas_realizadas_section(self):
        self.vendas_realizadas_frame = tk.Frame(self.root, bg="#e0f7fa")
        tk.Label(self.vendas_realizadas_frame, text="Vendas Realizadas", font=("Arial", 14), bg="#e0f7fa", fg="#00796b").pack()

        self.vendas_table = ttk.Treeview(self.vendas_realizadas_frame, columns=("Cliente", "Código", "Descrição", "Quantidade", "Total"), show="headings")
        for col in self.vendas_table["columns"]:
            self.vendas_table.heading(col, text=col)
            self.vendas_table.column(col, width=100)
        self.vendas_table.pack()

    def update_vendas_table(self):
        for i in self.vendas_table.get_children():
            self.vendas_table.delete(i)

        for cliente in self.clientes.values():
            if cliente.compras:
                for compra in cliente.compras:
                    self.vendas_table.insert("", "end", values=(cliente.nome, compra['Código'], compra['Descrição'], compra['Quantidade'], compra['Total']))

if __name__ == "__main__":
    # Inicializando os produtos e o estoque
    produtos = [
    Produto(1, "Calça", 20, 112.00),
    Produto(2, "Camisa", 18, 95.00),
    Produto(3, "Bermuda", 23, 45.90),
    Produto(4, "Saia", 12, 169.00),
    Produto(5, "Blusa", 9, 120.00),
    Produto(6, "Moletom", 4, 120.00),
    Produto(7, "Meia", 17, 12.99),
    Produto(8, "Tênis", 8, 183.00),
    Produto(9, "Bota", 3, 219.90)
]

    estoque = Estoque(produtos)

    # Inicializando a aplicação
    root = tk.Tk()
    app = SistemaVendasApp(root, estoque)
    root.mainloop()