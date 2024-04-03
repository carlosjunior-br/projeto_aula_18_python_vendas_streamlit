import sqlite3

class Produto:
    def __init__(self, id: int, nome: str, descricao: str, quantidade_em_estoque: int, valor_unit: float):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.quantidade_em_estoque = quantidade_em_estoque
        self.valor_unit = valor_unit

class Vendas:
    def __init__(self, produto: str, quantidade: int, valor: float, data):
        self.produto = produto
        self.quantidade = quantidade
        self.valor = valor
        self.data = data

class BancoDeDados:
    def __init__(self, nome_banco):
        self.nome_banco = nome_banco
        self.conexao = None
        self.cursor = None

    def conectar(self):
        self.conexao = sqlite3.connect(self.nome_banco)
        self.cursor = self.conexao.cursor()

    def desconectar(self):
        if self.conexao:
            self.conexao.close()

    # Produtos
            
    def criar_tabela_produtos(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS produtos (
                                id INTEGER PRIMARY KEY,
                                nome TEXT NOT NULL,
                                descricao TEXT NOT NULL,
                                quantidade_em_estoque INTEGER NOT NULL,
                                valor_unit REAL NOT NULL)''')
        self.conexao.commit()

    def inserir_produto(self, nome: str, descricao: str, quantidade_em_estoque: int, valor_unit: float):
        self.cursor.execute('''INSERT INTO produtos (nome, descricao, quantidade_em_estoque, valor_unit)
                            VALUES (?, ?, ?, ?)''', (nome, descricao, quantidade_em_estoque, valor_unit))
        self.conexao.commit()

    def excluir_produto(self, id):
        self.cursor.execute('''DELETE FROM produtos WHERE id = ?''', (id,))
        self.conexao.commit()

    def listar_produtos(self):
        self.cursor.execute('''SELECT * FROM produtos''')
        produtos = self.cursor.fetchall()
        return sorted([Produto(*produto) for produto in produtos], key=lambda x: x.nome)
    
    def listar_produtos_com_estoque(self):
        self.cursor.execute('''SELECT * FROM produtos WHERE quantidade_em_estoque>0''')
        produtos = self.cursor.fetchall()
        return sorted([Produto(*produto) for produto in produtos], key=lambda x: x.nome)
    
    def altera_produto(self, id, nome, descricao, quantidade, valor):
        self.cursor.execute('''UPDATE produtos SET nome=?,
                            descricao=?,
                            quantidade_em_estoque=?,
                            valor_unit=? WHERE id=?''', (nome, descricao, quantidade, valor, id))
        self.conexao.commit()

    def atualiza_estoque_produto(self, id, quantidade):
        self.cursor.execute('''UPDATE produtos SET quantidade_em_estoque=?
                             WHERE id=?''', (quantidade, id))
        self.conexao.commit()

    # Vendas
            
    def criar_tabela_vendas(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS vendas (
                                id INTEGER PRIMARY KEY,
                                id_produto INTEGER NOT NULL,
                                quantidade INTEGER NOT NULL,
                                valor REAL NOT NULL,
                                data DATE NOT NULL,
                                FOREIGN KEY (id_produto) REFERENCES produtos(id))''')
        self.conexao.commit()

    def inserir_venda(self, id_produto, quantidade, valor, data):
        self.cursor.execute('''INSERT INTO vendas (id_produto, quantidade, valor, data)
                            VALUES (?, ?, ?, ?)''', (id_produto, quantidade, valor, data))
        self.conexao.commit()

    def listar_vendas(self):
        self.cursor.execute('''SELECT produtos.nome as produto, vendas.quantidade,
                            vendas.valor, strftime('%d/%m/%Y', vendas.data) as data_formatada 
                            FROM vendas INNER JOIN produtos ON produtos.id = vendas.id_produto''')
        vendas = self.cursor.fetchall()
        return [Vendas(*venda) for venda in vendas]