import locale
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import *
from modulos.banco_de_dados import *
import base64

# Definir o título do aplicativo:
titulo_app = "Sistema de Gerenciamento de Estoque"
st.set_page_config(
    page_title=titulo_app,
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded"
    # menu_items={
    #     'Get Help': 'https://www.extremelycoolapp.com/help',
    #     'Report a bug': "https://www.extremelycoolapp.com/bug",
    #     'About': "# This is a header. This is an *extremely* cool app!"
    # }
)

# Configurar a localização para o Brasil (pt_BR)
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Configurar o CSS
with open("styles.css") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)
    
# Configurando o objeto banco de dados
banco = BancoDeDados('vendas_bd.sqlite')
banco.conectar()
banco.criar_tabela_produtos()
banco.criar_tabela_vendas()

def formato_moeda(valor):
    return locale.currency(valor, grouping=True, symbol='R$')

def renderizar():
    st.experimental_rerun()

def popup_e_renderizar(mensagem):
    # Criação de um elemento vazio para posteriormente substituir o conteúdo com o popup
    popup_container = st.empty()

    # Adicionando conteúdo ao popup
    popup_container.warning(mensagem)

    # Botão para fechar o popup
    if st.button("OK", key="botao_popup_e_renderizar"):
        # Limpando o conteúdo do elemento vazio para fechar o popup
        popup_container.empty()
        renderizar()

def popup(mensagem):
    # Criação de um elemento vazio para posteriormente substituir o conteúdo com o popup
    popup_container = st.empty()

    # Adicionando conteúdo ao popup
    popup_container.warning(mensagem)

    # Botão para fechar o popup
    if st.button("OK", key="botao_popup"):
        # Limpando o conteúdo do elemento vazio para fechar o popup
        popup_container.empty()

def validar_cadastro(nome, descricao, quantidade, valor):
    if not nome:
        st.warning('Por favor, insira o nome do produto.')
        return False
    if not descricao:
        st.warning('Por favor, insira a descrição do produto.')
        return False
    if quantidade <= 0 or not isinstance(quantidade, int):
        st.warning('A quantidade em estoque deve ser um número inteiro positivo.')
        return False
    if valor <= 0.0 or not isinstance(valor, float):
        st.warning('O valor unitário deve ser um número decimal positivo.')
        return False
    return True

# Menu Cadastro de produtos
def cadastro_de_produtos():
    
    def limpar_campos_produto():
        st.session_state["nome"] = None
        st.session_state["descricao"] = None
        st.session_state["quantidade"] = None
        st.session_state["valor"] = None

    def produto_existe(lista_de_produtos, recebe_nome):
        produto_ja_cadastrado = next((p for p in lista_de_produtos if p.nome.upper() == recebe_nome.upper()), None)
        if produto_ja_cadastrado:
            return True
        else:
            return False

    st.title(f"{lista_opcoes_menu[1].upper()}", anchor="titulos")

    recebe_nome = st.text_input("Nome do produto:", key="nome")
    recebe_descricao = st.text_area("Descrição do produto:", key="descricao")
    recebe_quantidade = st.number_input("Quantidade em estoque:", step=1, key="quantidade", min_value=1)
    recebe_valor = st.number_input("Valor unitário: R$", format="%.2f", step=0.1, key="valor", min_value=0.01)
    col1, col2 = st.columns(2)
    botao_cadastrar = col1.button("Cadastrar", key="botao_cadastrar")
    botao_limpar = col2.button(label="Limpar", on_click=limpar_campos_produto, key="botao_limpar")
    if botao_limpar:
        st.success(f"Todos os campos foram limpados com sucesso!")
    if botao_cadastrar:
        if  produto_existe(banco.listar_produtos(), recebe_nome):
            st.warning(f"O produto {recebe_nome.upper()} já existe no cadastro!")
        else:
            if validar_cadastro(recebe_nome, recebe_descricao, recebe_quantidade, recebe_valor):
                banco.inserir_produto(recebe_nome, recebe_descricao, recebe_quantidade, recebe_valor)
                st.success(f"O produto {recebe_nome.upper()} foi cadastrado com sucesso!")

# Menu vendas
def vendas():
    
    def validar_venda(quantidade_venda, quantidade_estoque):
        if quantidade_venda <= 0 or not isinstance(quantidade_venda, int) or quantidade_venda > quantidade_estoque:
            st.warning('Quantidade inválida! Favor revisar.')
            return False
        return True
    
    st.title(f"{lista_opcoes_menu[2].upper()}", anchor="titulos")

    lista_de_produtos = banco.listar_produtos_com_estoque()
    if len(lista_de_produtos) == 0:
        st.warning("Não existe nenhum produto com estoque!")
    else:
        lista_de_nomes_produtos = [f"{produto.nome} | Estoque: {produto.quantidade_em_estoque} | Valor: {formato_moeda(produto.valor_unit)}" for produto in lista_de_produtos]
        recebe_produto = st.selectbox("Selecione o produto a ser vendido:", lista_de_nomes_produtos, key="produto")
        indice_produto_selecionado = lista_de_nomes_produtos.index(recebe_produto)
        recebe_id_produto = lista_de_produtos[indice_produto_selecionado].id
        recebe_valor_unitario = lista_de_produtos[indice_produto_selecionado].valor_unit
        st.write(f"Valor unitário: {formato_moeda(lista_de_produtos[indice_produto_selecionado].valor_unit)}")
        recebe_quantidade = st.number_input("Quantidade:", step=1, key="quantidade", min_value=1, max_value=lista_de_produtos[indice_produto_selecionado].quantidade_em_estoque)
        recebe_valor = round(recebe_valor_unitario * recebe_quantidade, 2)
        st.write(f"Valor total da venda: {formato_moeda(recebe_valor)}")
        recebe_data = st.date_input("Data da venda: ", key="data", value='today', format='DD/MM/YYYY')
        botao_vender_container = st.empty()
        botao_vender = botao_vender_container.button("Efetuar a venda", key="botao_vender")
        if botao_vender:
            if validar_venda(recebe_quantidade, lista_de_produtos[indice_produto_selecionado].quantidade_em_estoque):
                banco.inserir_venda(lista_de_produtos[indice_produto_selecionado].id, recebe_quantidade, recebe_valor, recebe_data)
                nova_quantidade_estoque = lista_de_produtos[indice_produto_selecionado].quantidade_em_estoque - recebe_quantidade
                banco.atualiza_estoque_produto(recebe_id_produto, nova_quantidade_estoque)
                if nova_quantidade_estoque == 0:
                    st.warning(f"O estoque do produto {lista_de_produtos[indice_produto_selecionado].nome.upper()} está esgotado!")        
                botao_vender_container.empty()
                popup_e_renderizar(f"A venda do produto {lista_de_produtos[indice_produto_selecionado].nome.upper()} foi realizada com sucesso!\nClique em OK para continuar.")

# Menu atualizacao de produtos
def atualizacao_de_produtos():
    
    st.title(f"{lista_opcoes_menu[3].upper()}", anchor="titulos")

    lista_de_produtos = banco.listar_produtos()
    if len(lista_de_produtos) == 0:
        st.warning("Não existe nenhum produto cadastrado!")
    else:
        lista_de_nomes_produtos = [f"{produto.nome}" for produto in lista_de_produtos]
        recebe_produto = st.selectbox("Selecione o produto a ser atualizado:", lista_de_nomes_produtos, key="produto")
        indice_produto_selecionado = lista_de_nomes_produtos.index(recebe_produto)
        recebe_id_produto = lista_de_produtos[indice_produto_selecionado].id
        recebe_nome = st.text_input("Nome do produto:", key="novo_nome", value=lista_de_produtos[indice_produto_selecionado].nome)
        recebe_descricao = st.text_area("Descrição do produto:", key="nova_descricao", value=lista_de_produtos[indice_produto_selecionado].descricao)
        # Tratamento para quando a quantidade em estoque for 0
        nova_quantidade = lista_de_produtos[indice_produto_selecionado].quantidade_em_estoque
        if lista_de_produtos[indice_produto_selecionado].quantidade_em_estoque == 0:
            nova_quantidade = 1
        recebe_quantidade = st.number_input("Quantidade em estoque:", step=1, key="nova_quantidade", min_value=1, value=nova_quantidade)
        recebe_valor = st.number_input("Valor unitário: R$", format="%.2f", step=0.1, key="novo_valor", min_value=0.01, value=lista_de_produtos[indice_produto_selecionado].valor_unit)
        botoes_atualizar_produto_container = st.empty()
        col1, col2 = botoes_atualizar_produto_container.columns(2)
        botao_salvar = col1.button("Salvar", key="botao_salvar")
        botao_excluir = col2.button("Excluir produto", key="botao_excluir")
        if botao_salvar:
            if validar_cadastro(recebe_nome, recebe_descricao, recebe_quantidade, recebe_valor):
                botoes_atualizar_produto_container.empty()
                banco.altera_produto(recebe_id_produto, recebe_nome, recebe_descricao, recebe_quantidade, recebe_valor)
                popup_e_renderizar(f"O produto {recebe_nome.upper()} foi atualizado com sucesso!\nClique em OK para continuar.")
        if botao_excluir:
            botoes_atualizar_produto_container.empty()
            banco.excluir_produto(recebe_id_produto)
            popup_e_renderizar(f"O produto {lista_de_produtos[indice_produto_selecionado].nome.upper()} foi exclído com sucesso!\nClique em OK para continuar.")

# Menu lista de produtos
def lista_de_produtos():
    
    # Nas funções de filtros, lembrar de usar os nomes de campo do dicionário e não do objeto
    
    st.title(f"{lista_opcoes_menu[4].upper()}", anchor="titulos")

    lista_de_produtos = banco.listar_produtos()
    if len(lista_de_produtos) == 0:
        st.warning("Não existe nenhum produto cadastrado!")
    else:
        produtos_formatados = pd.DataFrame({
            'Nome': [produto.nome for produto in lista_de_produtos],
            'Descrição': [produto.descricao for produto in lista_de_produtos],
            'Quantidade em estoque': [produto.quantidade_em_estoque for produto in lista_de_produtos],
            'Valor unitário R$': [produto.valor_unit for produto in lista_de_produtos],
            'Valor total R$': [round(produto.quantidade_em_estoque * produto.valor_unit, 2) for produto in lista_de_produtos]
        })
        
        st.write("Filtros de dados disponíveis:")
        opcoes_de_filtro = ["Por quantidade", "Por valor unitário", "Por valor total", "Por nome", "Por descrição"]
        filtro_quantidade = st.checkbox(opcoes_de_filtro[0])
        filtro_valor = st.checkbox(opcoes_de_filtro[1])
        filtro_total = st.checkbox(opcoes_de_filtro[2])
        filtro_nome = st.checkbox(opcoes_de_filtro[3])
        filtro_descricao = st.checkbox(opcoes_de_filtro[4])
        
        df_filtrado = produtos_formatados  # DataFrame inicialmente não filtrado
        
        if filtro_quantidade:
            col1, col2 = st.columns(2)
            quant_inicial = col1.number_input("Quantidade em estoque inicial:", step=1, min_value=0, value=0)
            quant_final = col2.number_input("Quantidade em estoque final:", step=1, min_value=0, value=100)
            df_filtrado = df_filtrado[(df_filtrado['Quantidade em estoque'] >= quant_inicial) & (df_filtrado['Quantidade em estoque'] <= quant_final)]
        
        if filtro_valor:
            col1, col2 = st.columns(2)
            valor_inicial = col1.number_input("Valor unitário inicial: R$", format="%.2f", step=0.1, min_value=0.00, value=0.00)
            valor_final = col2.number_input("Valor unitário final: R$", format="%.2f", step=0.1, min_value=0.00, value=100.00)
            df_filtrado = df_filtrado[(df_filtrado['Valor unitário R$'] >= valor_inicial) & (df_filtrado['Valor unitário R$'] <= valor_final)]
        
        if filtro_total:
            col1, col2 = st.columns(2)
            valor_inicial = col1.number_input("Valor total inicial: R$", format="%.2f", step=0.1, min_value=0.00, value=0.00)
            valor_final = col2.number_input("Valor total final: R$", format="%.2f", step=0.1, min_value=0.00, value=1000.00)
            df_filtrado = df_filtrado[(df_filtrado['Valor total R$'] >= valor_inicial) & (df_filtrado['Valor total R$'] <= valor_final)]
        
        if filtro_nome:
            nome = st.text_input("Qualquer parte do nome:", value="")
            df_filtrado = df_filtrado[(df_filtrado['Nome'].str.contains(nome, case=False))]
        
        if filtro_descricao:
            descricao = st.text_input("Qualquer parte da descrição:", value="")
            df_filtrado = df_filtrado[(df_filtrado['Descrição'].str.contains(descricao, case=False))]

        st.dataframe(df_filtrado.style.format({'Quantidade em estoque': '{:.0f}', 'Valor unitário R$': '{:.2f}', 'Valor total R$': '{:.2f}'}), hide_index=True)
        st.write("**TOTAL GERAL**")
        st.write(f"**Quantidade em estoque:** {df_filtrado['Quantidade em estoque'].sum():.0f}")
        st.write(f"**Valor total:** R$ {df_filtrado['Valor total R$'].sum():.2f}")
        if st.button("Criar arquivo em excel"):
            # Define o nome do arquivo
            nome_arquivo = 'meu_dataframe.xlsx'
            # Salva o DataFrame em um arquivo Excel
            df_filtrado.to_excel(nome_arquivo, index=False)
            # Lê o arquivo Excel como bytes
            with open(nome_arquivo, 'rb') as f:
                bytes_arquivo = f.read()
            # Codifica o arquivo em base64
            bytes_codificados = base64.b64encode(bytes_arquivo).decode()
            # Cria o link de download do arquivo
            link_download = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{bytes_codificados}" download="{nome_arquivo}" id="meu-link">Baixar o arquivo</a>'
            # Exibe o link no Streamlit
            st.markdown(link_download, unsafe_allow_html=True)
        
# Menu lista de vendas
def lista_de_vendas():
    st.title(f"{lista_opcoes_menu[5].upper()}", anchor="titulos")

    lista_de_vendas = banco.listar_vendas()
    if len(lista_de_vendas) == 0:
        st.warning("Não existe nenhuma venda cadastrada!")
    else:
        vendas_formatadas = pd.DataFrame({
            'Produto': [venda.produto for venda in lista_de_vendas],
            'Quantidade': [venda.quantidade for venda in lista_de_vendas],
            'Valor R$': [venda.valor for venda in lista_de_vendas],
            'Data': [venda.data for venda in lista_de_vendas]
        })
        vendas_formatadas['Data'] = pd.to_datetime(vendas_formatadas['Data'], format='%d/%m/%Y')
        
        st.write("Filtros de dados disponíveis:")
        opcoes_de_filtro = ["Por quantidade", "Por valor", "Por produto", "Por data"]
        filtro_quantidade = st.checkbox(opcoes_de_filtro[0])
        filtro_valor = st.checkbox(opcoes_de_filtro[1])
        filtro_produto = st.checkbox(opcoes_de_filtro[2])
        filtro_data = st.checkbox(opcoes_de_filtro[3])
        
        df_filtrado = vendas_formatadas  # DataFrame inicialmente não filtrado
        
        if filtro_quantidade:
            col1, col2 = st.columns(2)
            quant_inicial = col1.number_input("Quantidade inicial:", step=1, min_value=0, value=0)
            quant_final = col2.number_input("Quantidade final:", step=1, min_value=0, value=100)
            df_filtrado = df_filtrado[(df_filtrado['Quantidade'] >= quant_inicial) & (df_filtrado['Quantidade'] <= quant_final)]
        
        if filtro_valor:
            col1, col2 = st.columns(2)
            valor_inicial = col1.number_input("Valor inicial: R$", format="%.2f", step=0.1, min_value=0.00, value=0.00)
            valor_final = col2.number_input("Valor final: R$", format="%.2f", step=0.1, min_value=0.00, value=1000.00)
            df_filtrado = df_filtrado[(df_filtrado['Valor R$'] >= valor_inicial) & (df_filtrado['Valor R$'] <= valor_final)]
        
        if filtro_produto:
            nome = st.text_input("Qualquer parte do nome do produto:", value="")
            df_filtrado = df_filtrado[(df_filtrado['Produto'].str.contains(nome, case=False))]
        
        if filtro_data:
            col1, col2 = st.columns(2)
            data_inicial = col1.date_input("Data inicial:", value=date(2000, 1, 1), format='DD/MM/YYYY')
            data_final = col2.date_input("Data final:", value=date.today(), format='DD/MM/YYYY')
            df_filtrado = df_filtrado[(df_filtrado['Data'] >= datetime.combine(data_inicial, datetime.min.time())) & (df_filtrado['Data'] <= datetime.combine(data_final, datetime.max.time()))]
        
        st.dataframe(df_filtrado.style.format({'Quantidade': '{:.0f}', 'Valor R$': '{:.2f}', 'Data': lambda x: x.strftime('%d/%m/%Y')}), hide_index=True)
        st.write("**TOTAL GERAL**")
        st.write(f"**Quantidade:** {df_filtrado['Quantidade'].sum():.0f}")
        st.write(f"**Valor:** R$ {df_filtrado['Valor R$'].sum():.2f}")
        if st.button("Criar arquivo em excel"):
            # Define o nome do arquivo
            nome_arquivo = 'meu_dataframe.xlsx'
            # Salva o DataFrame em um arquivo Excel
            df_filtrado.to_excel(nome_arquivo, index=False)
            # Lê o arquivo Excel como bytes
            with open(nome_arquivo, 'rb') as f:
                bytes_arquivo = f.read()
            # Codifica o arquivo em base64
            bytes_codificados = base64.b64encode(bytes_arquivo).decode()
            # Cria o link de download do arquivo
            link_download = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{bytes_codificados}" download="{nome_arquivo}" id="meu-link">Baixar o arquivo</a>'
            # Exibe o link no Streamlit
            st.markdown(link_download, unsafe_allow_html=True)

# Definir os itens do menu de navegação:
lista_opcoes_menu = ["Página inicial", "Cadastro de produtos", "Vendas", "Atualização de produtos", "Lista de produtos", "Lista de vendas"]

with st.sidebar:
    opcao = option_menu(
        menu_title=titulo_app,
        options=lista_opcoes_menu,
        icons=['house', 'floppy', 'cart', 'floppy-fill', 'receipt', 'receipt'],
        menu_icon="database",
        default_index=0,
        #orientation="horizontal",
        styles={
            "menu-title": {"font-size": "14px", "text-align": "center"},
            "nav-link": {"font-size": "12px", "text-align": "left", "margin":"0px", "--hover-color": "#ff9898"},
            "nav-link-selected": {"background-color": "red"},
        }
    )

if opcao == lista_opcoes_menu[0]:
    st.title(f"Você está na página inicial! Navegue pelas opções através do menu lateral.".upper(), anchor="titulos")

if opcao == lista_opcoes_menu[1]:
    cadastro_de_produtos()

if opcao == lista_opcoes_menu[2]:
    vendas()

if opcao == lista_opcoes_menu[3]:
    atualizacao_de_produtos()

if opcao == lista_opcoes_menu[4]:
    lista_de_produtos()
    
if opcao == lista_opcoes_menu[5]:
    lista_de_vendas()

banco.desconectar()
