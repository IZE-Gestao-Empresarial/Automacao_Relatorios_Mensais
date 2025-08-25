#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Formulário Streamlit - Relatórios Mensais
Interface web para coletar dados sobre relatórios de clientes.

Uso: 
  streamlit run formulario_streamlit.py
  streamlit run formulario_streamlit.py "Cliente A" "Cliente B" "Cliente C"

Exemplo:
  streamlit run formulario_streamlit.py "Ativa" "Roma" "Biomassa"
"""

import streamlit as st
import json
from datetime import datetime
import pandas as pd
import sys
import os
import threading
import time
import gspread
from google.oauth2.service_account import Credentials

def configurar_google_sheets():
    """
    Configura a conexão com o Google Sheets
    """
    try:
        # Definir escopos necessários
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Tentar usar secrets do Streamlit primeiro (para produção)
        try:
            credentials_dict = st.secrets["gcp_service_account"]
            credentials = Credentials.from_service_account_info(
                credentials_dict, 
                scopes=scopes
            )
        except (KeyError, FileNotFoundError):
            # Fallback para arquivo local (para desenvolvimento)
            if os.path.exists("api-do-drive.json"):
                credentials = Credentials.from_service_account_file(
                    "api-do-drive.json", 
                    scopes=scopes
                )
            else:
                st.error("❌ Credenciais não encontradas. Configure os secrets no Streamlit Cloud ou adicione o arquivo 'api-do-drive.json' localmente.")
                return None
        
        # Autorizar cliente
        client = gspread.authorize(credentials)
        
        # Testar conexão tentando acessar a planilha
        try:
            sheet_id = "13jj-F3gBIkRoLPjT05x2A_JVXa6BlrXQWpvdRLVkmcw"
            test_spreadsheet = client.open_by_key(sheet_id)
            test_worksheet = test_spreadsheet.worksheet("Respostas Formulário")
            # Se chegou até aqui, a conexão está funcionando
        except Exception as e:
            st.error(f"❌ Erro ao acessar a planilha: {str(e)}")
            st.error("🔍 Verifique se o ID da planilha está correto e se as permissões estão configuradas")
            return None
        
        return client
    except FileNotFoundError as e:
        st.error(f"❌ Arquivo de credenciais não encontrado: {e}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"❌ Erro ao ler arquivo JSON de credenciais: {e}")
        st.error("🔍 Verifique se o arquivo 'api-do-drive.json' está com formato válido")
        return None
    except Exception as e:
        st.error(f"❌ Erro ao configurar Google Sheets:")
        st.error(f"📋 Detalhes: {str(e)}")
        st.error(f"🔧 Tipo do erro: {type(e).__name__}")
        return None

def enviar_para_google_sheets(dados_exportacao):
    """
    Envia os dados do formulário para o Google Sheets
    """
    try:
        # Configurar conexão
        client = configurar_google_sheets()
        
        if client is None:
            st.error("❌ Não foi possível conectar ao Google Sheets")
            return False
            
        # Abrir a planilha
        sheet_id = "13jj-F3gBIkRoLPjT05x2A_JVXa6BlrXQWpvdRLVkmcw"
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.worksheet("Respostas Formulário")
        
        # Preparar dados para inserção
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Para cada cliente com resposta "Sim", adicionar uma linha
        for cliente_dados in dados_exportacao["clientes_sim"]:
            linha = [
                timestamp,  # Data/Hora
                cliente_dados["cliente"],  # Nome do Cliente
                "Sim",  # Solicita Relatório
                ", ".join(cliente_dados["modulos"]) if cliente_dados["modulos"] else "Nenhum",  # Módulos
                cliente_dados["nota_consultor"] if cliente_dados["nota_consultor"] else ""  # Observações
            ]
            worksheet.append_row(linha)
        
        # Para cada cliente com resposta "Não", adicionar uma linha
        for cliente_nao in dados_exportacao["clientes_nao"]:
            linha = [
                timestamp,  # Data/Hora
                cliente_nao,  # Nome do Cliente
                "Não",  # Solicita Relatório
                "",  # Módulos (vazio)
                ""  # Observações (vazio)
            ]
            worksheet.append_row(linha)
        
        return True
        
    except Exception as e:
        st.error(f"❌ Erro ao enviar dados para o Google Sheets: {str(e)}")
        st.error(f"🔧 Tipo do erro: {type(e).__name__}")
        return False

def configurar_pagina():
    """
    Configurações da página Streamlit
    """
    st.set_page_config(
        page_title="Formulário de envio dos Relatórios Mensais",
        page_icon="📊",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # CSS personalizado para design profissional - Paleta FF6900 + Tema Claro
    st.markdown("""
    <style>
    /* Forçar tema claro */
    .stApp {
        background-color: #fdf7f4 !important;
        color: #262730 !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
    }
    
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    .main {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: #fdf7f4 !important;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 800px;
    }
    
    h1 {
        color: #FF6900;
        text-align: center;
        font-weight: 600;
        margin-bottom: 0.5rem;
        text-shadow: 1px 1px 2px rgba(255, 105, 0, 0.1);
    }
    
    h3 {
        color: #CC5500;
        font-weight: 500;
        border-bottom: 2px solid #FFE5D6;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    
    .client-section {
        background-color: white;
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(255, 105, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid #FF6900;
        border-top: 1px solid #FFE5D6;
    }
    
    .instructions {
        background: linear-gradient(135deg, #FFF4E6 0%, #FFE5D6 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #FF6900;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(255, 105, 0, 0.08);
    }
    
    .success-message {
        background: linear-gradient(135deg, #E8F5E8 0%, #D4F1D4 100%);
        border: 1px solid #66BB6A;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #2E7D32;
    }
    
    .warning-message {
        background: linear-gradient(135deg, #FFF8E1 0%, #FFECB3 100%);
        border: 1px solid #FFB74D;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #E65100;
    }
    
    .error-message {
        background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%);
        border: 1px solid #E57373;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #C62828;
    }
    
    /* Personalização dos botões */
    .stButton > button {
        background: linear-gradient(135deg, #FF6900 0%, #FF8533 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(255, 105, 0, 0.3) !important;
        height: 2.8rem !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #E55A00 0%, #FF6900 100%) !important;
        box-shadow: 0 4px 16px rgba(255, 105, 0, 0.4) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Botão secundário para novo formulário */
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #6C757D 0%, #5A6268 100%) !important;
        color: white !important;
        border: none !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #5A6268 0%, #495057 100%) !important;
    }
    
    /* Personalização dos selectboxes */
    .stSelectbox > div > div {
        border-color: #FFB366 !important;
        background-color: white !important;
        color: #262730 !important;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #FF6900 !important;
        box-shadow: 0 0 0 2px rgba(255, 105, 0, 0.2) !important;
    }
    
    /* Personalização dos checkboxes */    
    .stCheckbox > label > div[data-checked="true"] {
        background-color: #FF6900 !important;
        border-color: #FF6900 !important;
    }
    
    /* Personalização dos text areas */
    .stTextArea > div > div > textarea {
        background-color: white !important;
        color: #262730 !important;
        border-color: #FFB366 !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #FF6900 !important;
        box-shadow: 0 0 0 2px rgba(255, 105, 0, 0.2) !important;
    }
    
    /* Garantir que todos os textos sejam escuros */
    .stMarkdown, .stText, p, span, div {
        color: #262730 !important;
    }
    
    /* Forçar fundo claro nos containers */
    .block-container {
        background-color: #fdf7f4 !important;
    }
    </style>
    """, unsafe_allow_html=True)

def verificar_permissoes_planilha():
    """
    Exibe instruções para configurar as permissões da planilha
    """
    st.markdown("---")
    st.markdown("### 🔧 Configuração de Permissões")
    
    st.info("""
    **Para resolver o erro de permissão, siga estes passos:**
    
    1. 📂 Abra sua planilha no Google Sheets
    2. 🔗 Clique em "Compartilhar" (canto superior direito)
    3. 📧 Adicione este email: `conex-o-drive@api-do-drive-para-o-python.iam.gserviceaccount.com`
    4. ⚙️ Defina a permissão como "Editor"
    5. ✅ Clique em "Enviar"
    
    **Verifique também:**
    - ✅ A planilha tem o ID correto: `13jj-F3gBIkRoLPjT05x2A_JVXa6BlrXQWpvdRLVkmcw`
    - ✅ Existe uma aba chamada exatamente "Respostas Formulário"
    """)

def cabecalho():
    """
    Cabeçalho da aplicação
    """
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1>Formulário de Relatórios Mensais</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="instructions">
        <h4 style="margin-top: 0; color: #FF6900;">Instruções de Preenchimento:</h4>
        <ol style="margin-bottom: 0;">
            <li><strong>Selecione</strong> os clientes que deseja enviar o relatório</li>
            <li><strong>Escolha os módulos</strong> necessários quando aplicável</li>
            <li><strong>Adicione observações</strong> se necessário</li>
            <li><strong>Envie</strong> o formulário</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

def inicializar_clientes():
    """
    Inicializa a lista de clientes com valores dos parâmetros do terminal
    """
    # Definir lista fixa de clientes diretamente no código
    if 'clientes' not in st.session_state:
        clientes_args = ["Fio de Amor", "Saquecred", "Connect Energia Solar"]
        st.session_state.clientes = clientes_args

def formulario_principal():
    """
    Formulário principal em formato profissional
    """
    # Inicializar clientes pré-definidos
    inicializar_clientes()
    
    # Inicializar respostas na sessão
    if 'respostas_formulario' not in st.session_state:
        st.session_state.respostas_formulario = {}
    
    respostas = {}
    
    # Formulário em formato profissional
    for i, cliente in enumerate(st.session_state.clientes):
        # Container com estilo profissional
        st.markdown(f"""
        <div class="client-section">
            <h4 style="margin-top: 0; color: #FF6900; font-size: 1.2rem;">{cliente}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            # Pergunta principal
            col1, col2 = st.columns([1, 2])
            
            with col1:
                deseja_relatorio = st.selectbox(
                    "Solicitar relatório:",
                    options=["Selecione uma opção", "Sim", "Não"],
                    key=f"relatorio_{i}",
                )
            
            with col2:
                if deseja_relatorio != "Selecione uma opção":
                    if deseja_relatorio == "Sim":
                        st.markdown('<div class="success-message">Relatório será gerado</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="error-message">Relatório não solicitado</div>', unsafe_allow_html=True)
            
            # Configurações detalhadas para "Sim"
            modulos_selecionados = []
            nota_consultor = ""
            
            if deseja_relatorio == "Sim":
                st.markdown("**Módulos a incluir no relatório:**")
                
                col_fc, col_dre, col_ind = st.columns(3)
                
                with col_fc:
                    fc_check = st.checkbox(
                        "FC", 
                        key=f"fc_{i}",
                    )
                with col_dre:
                    dre_check = st.checkbox(
                        "DRE", 
                        key=f"dre_{i}",

                    )
                with col_ind:
                    ind_check = st.checkbox(
                        "Indicadores", 
                        key=f"ind_{i}",

                    )
                
                # Construir lista de módulos
                if fc_check:
                    modulos_selecionados.append("FC")
                if dre_check:
                    modulos_selecionados.append("DRE")
                if ind_check:
                    modulos_selecionados.append("Indicadores")
                
                # Campo de observações
                nota_consultor = st.text_area(
                    "Nota do Consultor:",
                    placeholder="Digite aqui as suas observações adicionais para o relatório...",
                    height=80,
                    key=f"nota_{i}",
                )
                
                # Validação
                if not modulos_selecionados:
                    st.markdown('<div class="warning-message">Selecione pelo menos um módulo para gerar o relatório</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="success-message">Módulos selecionados: {", ".join(modulos_selecionados)}</div>', unsafe_allow_html=True)
            
            # Armazenar resposta
            respostas[cliente] = {
                "deseja_relatorio": deseja_relatorio,
                "modulos": modulos_selecionados,
                "nota_consultor": nota_consultor
            }
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    return respostas


def processar_formulario_backend(respostas):
    """
    Processa as respostas e envia os dados para o Google Sheets
    """
    # Validar se há respostas
    respostas_validas = {k: v for k, v in respostas.items() if v["deseja_relatorio"] != "Selecione uma opção"}
    
    if not respostas_validas:
        return None
    
    # Separar clientes por resposta
    clientes_sim = []
    clientes_nao = []
    
    for cliente, dados in respostas_validas.items():
        if dados["deseja_relatorio"] == "Sim":
            clientes_sim.append({
                "cliente": cliente,
                "modulos": dados["modulos"],
                "nota_consultor": dados["nota_consultor"]
            })
        else:
            clientes_nao.append(cliente)
    
    # Dados para exportação
    dados_exportacao = {
        "timestamp": datetime.now().isoformat(),
        "data_processamento": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "clientes_sim": clientes_sim,
        "clientes_nao": clientes_nao,
        "total_clientes": len(respostas_validas),
        "total_com_relatorio": len(clientes_sim),
        "total_sem_relatorio": len(clientes_nao),
        "taxa_solicitacao": (len(clientes_sim) / len(respostas_validas)) * 100 if len(respostas_validas) > 0 else 0
    }
    
    # Enviar dados para Google Sheets
    sucesso_sheets = enviar_para_google_sheets(dados_exportacao)
    
    # Só retornar dados se o envio foi bem-sucedido
    if sucesso_sheets:
        return dados_exportacao
    else:
        st.error("❌ Falha ao enviar os dados para o Google Sheets. Tente novamente.")
        return None

def exibir_confirmacao_envio():
    """
    Exibe confirmação simples de envio com opção de novo formulário
    """
    st.markdown("---")
    st.success("✅ **Formulário enviado com sucesso!**")
    
    # Botão estilizado para novo formulário
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Preencher Novo Formulário", 
                    type="secondary", 
                    use_container_width=True,
                    help="Limpa os dados atuais e permite preencher um novo formulário"):
            # Limpar dados processados
            if 'dados_processados' in st.session_state:
                del st.session_state.dados_processados
            
            # Limpar respostas do formulário
            if 'respostas_formulario' in st.session_state:
                del st.session_state.respostas_formulario
            
            # Reexecutar aplicação
            st.rerun()
    

def verificar_acesso():
    """
    Verifica se o parâmetro is_consultant=true está presente na URL
    """
    try:
        query_params = st.query_params
        is_consultant = query_params.get('is_consultant', 'false')
    except AttributeError:
        # Fallback para versão mais antiga do Streamlit
        query_params = st.experimental_get_query_params()
        is_consultant = query_params.get('is_consultant', ['false'])
        if isinstance(is_consultant, list):
            is_consultant = is_consultant[0] if is_consultant else 'false'
    
    return str(is_consultant).lower() == 'true'

def exibir_acesso_negado():
    """
    Exibe tela de acesso negado
    """
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0; color: #FF6900;">
        <h1>🚫 Acesso Negado</h1>
        <p style="font-size: 1.2rem; color: #666; margin-top: 2rem;">
            Você não tem permissão para acessar este formulário.
        </p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """
    Função principal da aplicação Streamlit
    """
    configurar_pagina()
    
    # Verificar acesso antes de exibir o formulário
    if not verificar_acesso():
        exibir_acesso_negado()
        return
    
    cabecalho()
    
    # Formulário principal
    respostas = formulario_principal()
    
    if respostas:        
        # Verificar se há respostas válidas
        respostas_validas = {k: v for k, v in respostas.items() if v["deseja_relatorio"] != "Selecione uma opção"}
        
        if not respostas_validas:
            st.warning("⚠️ Complete o formulário para pelo menos um cliente antes de enviar!")
        else:
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                if st.button("📤 Enviar Formulário", type="primary", use_container_width=True):
                    dados_exportacao = processar_formulario_backend(respostas)
                    if dados_exportacao:
                        st.session_state.dados_processados = dados_exportacao
        
        # Mostrar confirmação se já foi processado
        if 'dados_processados' in st.session_state:
            exibir_confirmacao_envio()

if __name__ == "__main__":
    main()
