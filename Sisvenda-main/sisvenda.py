import sqlite3
from datetime import datetime

# ==========================================
# 1. CONFIGURAÇÃO DO BANCO DE DADOS
# ==========================================
def conectar():
    """Conecta ao banco de dados SQLite."""
    conn = sqlite3.connect('sisvenda.db')
    return conn

def criar_tabelas(conn):
    """Cria as tabelas necessárias para o sistema."""
    cursor = conn.cursor()
    
    # Tabela de Usuários (NOVO)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    ''')
    
    # Cria um usuário padrão caso não exista nenhum (NOVO)
    cursor.execute('SELECT COUNT(*) FROM usuarios')
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES ('admin', '1234')")
    
    # Tabela de Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT
        )
    ''')
    
    # Tabela de Produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            estoque INTEGER NOT NULL
        )
    ''')
    
    # Tabela de Vendas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            produto_id INTEGER,
            quantidade INTEGER NOT NULL,
            total REAL NOT NULL,
            data_venda TEXT NOT NULL,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id),
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    ''')
    conn.commit()

# ==========================================
# 2. FUNÇÕES DO SISTEMA (CRUD e Lógica)
# ==========================================
def fazer_login(conn):
    """Solicita usuário e senha antes de liberar o sistema."""
    print("\n" + "="*30)
    print("🔐 LOGIN - SISVENDA")
    print("="*30)
    
    while True:
        usuario = input("Usuário: ")
        senha = input("Senha: ")
        
        cursor = conn.cursor()
        # Verifica se o usuário e senha batem com o banco de dados
        cursor.execute('SELECT * FROM usuarios WHERE usuario = ? AND senha = ?', (usuario, senha))
        user = cursor.fetchone()
        
        if user:
            print(f"\n✅ Acesso liberado! Bem-vindo(a), {usuario}!")
            break
        else:
            print("\n❌ Usuário ou senha incorretos. Tente novamente.\n")

def cadastrar_cliente(conn, nome, telefone):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO clientes (nome, telefone) VALUES (?, ?)', (nome, telefone))
    conn.commit()
    print(f"\n✅ Cliente '{nome}' cadastrado com sucesso!")

def cadastrar_produto(conn, nome, preco, estoque):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)', (nome, preco, estoque))
    conn.commit()
    print(f"\n✅ Produto '{nome}' cadastrado com sucesso!")

def registrar_venda(conn, cliente_id, produto_id, quantidade):
    cursor = conn.cursor()
    
    cursor.execute('SELECT nome, preco, estoque FROM produtos WHERE id = ?', (produto_id,))
    produto = cursor.fetchone()
    
    if not produto:
        print("\n❌ Erro: Produto não encontrado.")
        return
        
    nome_prod, preco, estoque_atual = produto
    
    if estoque_atual < quantidade:
        print(f"\n❌ Erro: Estoque insuficiente! Estoque atual de {nome_prod}: {estoque_atual}")
        return
    
    cursor.execute('SELECT nome FROM clientes WHERE id = ?', (cliente_id,))
    cliente = cursor.fetchone()
    
    if not cliente:
        print("\n❌ Erro: Cliente não encontrado.")
        return
        
    total = preco * quantidade
    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO vendas (cliente_id, produto_id, quantidade, total, data_venda)
        VALUES (?, ?, ?, ?, ?)
    ''', (cliente_id, produto_id, quantidade, total, data_atual))
    
    novo_estoque = estoque_atual - quantidade
    cursor.execute('UPDATE produtos SET estoque = ? WHERE id = ?', (novo_estoque, produto_id))
    
    conn.commit()
    print(f"\n✅ Venda registrada! {quantidade}x {nome_prod} para {cliente[0]}. Total: R$ {total:.2f}")

def listar_vendas(conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT v.id, c.nome, p.nome, v.quantidade, v.total, v.data_venda
        FROM vendas v
        JOIN clientes c ON v.cliente_id = c.id
        JOIN produtos p ON v.produto_id = p.id
    ''')
    vendas = cursor.fetchall()
    
    print("\n--- 📋 RELATÓRIO DE VENDAS ---")
    if not vendas:
        print("Nenhuma venda registrada ainda.")
    for v in vendas:
        print(f"ID Venda: {v[0]} | Data: {v[5]}")
        print(f"Cliente: {v[1]} | Produto: {v[2]} | Qtd: {v[3]} | Total: R$ {v[4]:.2f}")
        print("-" * 30)

# ==========================================
# 3. MENU INTERATIVO
# ==========================================
def main():
    conn = conectar()
    criar_tabelas(conn)
    
    # Chama a tela de login ANTES de mostrar o menu
    fazer_login(conn)
    
    while True:
        print("\n" + "="*30)
        print("🛒 SISTEMA SISVENDA")
        print("="*30)
        print("1. Cadastrar Cliente")
        print("2. Cadastrar Produto")
        print("3. Registrar Venda")
        print("4. Relatório de Vendas")
        print("0. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == '1':
            nome = input("Nome do cliente: ")
            telefone = input("Telefone: ")
            cadastrar_cliente(conn, nome, telefone)
            
        elif opcao == '2':
            nome = input("Nome do produto: ")
            preco = float(input("Preço (ex: 10.50): "))
            estoque = int(input("Quantidade em estoque: "))
            cadastrar_produto(conn, nome, preco, estoque)
            
        elif opcao == '3':
            cliente_id = int(input("ID do Cliente: "))
            produto_id = int(input("ID do Produto: "))
            quantidade = int(input("Quantidade vendida: "))
            registrar_venda(conn, cliente_id, produto_id, quantidade)
            
        elif opcao == '4':
            listar_vendas(conn)
            
        elif opcao == '0':
            print("\nSaindo do sistema... Até logo!")
            conn.close()
            break
        else:
            print("\n❌ Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()