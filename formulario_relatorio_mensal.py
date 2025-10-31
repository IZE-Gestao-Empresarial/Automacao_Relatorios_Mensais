#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Formulário Streamlit - Relatórios Mensais
Interface web para coletar dados sobre relatórios de clientes.

Uso: 
  streamlit run formulario_relatorio_mensal_corrigido.py
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
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
import asyncio
import re

def limpar_emojis_e_caracteres_especiais(texto):
    """
    Remove emojis e caracteres especiais do texto, mantendo apenas caracteres alfanuméricos,
    pontuação básica e espaços em branco.
    """
    if not texto:
        return texto
    
    # Padrão para remover emojis e outros caracteres especiais Unicode
    # Mantém letras, números, pontuação básica e espaços
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"  # enclosed characters
        "\U0001F900-\U0001F9FF"  # supplemental symbols and pictographs
        "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-a
        "\U00002600-\U000026FF"  # miscellaneous symbols
        "\U00002700-\U000027BF"  # dingbats
        "]+", 
        flags=re.UNICODE
    )
    
    # Remove emojis
    texto_limpo = emoji_pattern.sub('', texto)
    
    # Remove caracteres de controle e outros caracteres não imprimíveis
    # mas mantém quebras de linha, tabs e espaços
    texto_limpo = re.sub(r'[^\x20-\x7E\n\r\t\u00C0-\u017F\u0100-\u024F]', '', texto_limpo)
    
    # Remove espaços múltiplos e limpa o texto
    texto_limpo = re.sub(r'\s+', ' ', texto_limpo).strip()
    
    return texto_limpo

# Dicionário de consultores e seus respectivos clientes
# A estrutura de lista com um dicionário foi simplificada para apenas um dicionário
CONSULTORES_CLIENTES = {
        "Leonardo Souto": [

            "Mundo das Pedras",

            "R7 Motors",
            "DAZAN EQUIPAMENTOS",
            "FG AUTO CENTER"
        ],
        "Nathalia Toledo": [

            "Linha por Linha",
            "Rs 2v Ventures Empreendimentos",
        ],
        "Drisi Rigamonti": [

            "Biomassa"
        ],
        "Tiago Alves de Oliveira": [
            "Fio de Amor",
            "Daniel Guimarães Advocacia",

            "HOTEL VILLAGIO D'ITALIA",
            "Crescendo na Fé Cursos Online",
            "Connect Energia Solar",
            "Petfeel Petcenter",
            "Cabrera's",

            "Rs 2v Ventures Empreendimentos",
            "TOTAL AR"
        ],
        "Lucas Oliveira": [
            "Cloud Treinamentos",
            "Pingo Distribuidora",
            "Smart Glass"
        ],
        "Romulo Chaul": [

            "Euro e Cia [Matriz]",
            "Euro e Cia [Florianopolis]",
            "Euro e Cia [Infoprodutos]",
            "MAD Engenharia",
            "Atacadão das Confecções Comércio",
            "Nobre Casa",
            "M F Construcoes e Utilidades",
            "Drogaria Menor Preço",
            "La Casa de Hambúrguer",
            "Blend BR [1]",
            "Blend BR [2]",
            "Pontes Sports"
        ],
        "Vitor": [
            "Levens e Lineker"
        ],
        "Ariana Fernandes": [
            "Casa da Manicure",
            "VET FAUNA PET SHOP",
            "Sallus",

            "Kairo Ícaro Advogados Associados",
            "Dias e Lima Advogados",
            "Milhã Net",
            "LADISCON MARKETING DIGITAL",

            "Body & Fit"
        ],
        "Ana Paula B Duarte": [

            "Multifiltros",
            "Sideraço S/A",
            "Sanear Brasil",
            "MF Comércio de Caminhões",
            "Baixada do Sol Restaurante e Churrascaria"
            ],
        "Matheus Firmino": [
            "Expertabi Assessoria Internacional",
            "Roma Comunicação"
        ],
        "Danilo Vaz": [
            "BBZ Advocacia",

            "Renan Maldonado Advogados",
            "Firme e Forte - Segurança e Terceirização",
            "Leonardo Rainan e Rodrigo Pinho advogados associados",

            "OPT.DOC. Gestão de Consultórios",
            "Cia Sat Gerenciamento Via Satelite"
        ],
        "Ylienney Archil": [

            "VMB Advocacia"
        ],
        "Kaio Rodrigues": [

        ],
        "William Alves da Silva": [

            "AGRI FACAS"
            ],
        "Guilherme Teixeira": [
            "Peterson & Escobar ADV",
            "Maia & Morgado Advogados Associados",
            "AR Advocacia Empresarial",
            "Ilir Advogados",
            "Fretou Brasil Logística",
            "Vinhal Batista Imoveis"
        ],
        "Gabriel Matias Vieira": [
            "R - FLEX",
            "Embratecc"
            ],
        "Adeilton Rufino da Silva": [
            "Telerad",
            "Distribuidora Hortybom",
            "JP Recicla",
            "Auto Posto Crisma",
            "Projector",
            "TSM COMERCIO DE SEMIJOIAS",
            "MACARRONADA ITALIANA",
            "R J Macedo Agropecuária",
            "Toruk Sushi"
        ],
        "Pedro de Carvalho Marques": [
            "Summer Auto Peças",

            "Marcia Pinto Gastronomia",
            "Santrack",
            "Flávia Ayres"
        ],
        "deborafigueredo.ize@gmail.com": [
            "Siligyn",

            "Pizzaria Kallebe",

            "Longevitale"
            ],
        "Nury Sato": [
            "D&J Urbanas Dedetização e Higienização"
        ],
        "Rayane Caroline Cândida de Amorim Oliveira": [
            "Renda Mais Transporte",
            "EG Transportes e Logísticas"
        ]
    }

def configurar_banco_dados():
    """
    Configura a conexão com o banco de dados PostgreSQL
    Retorna conexão se bem-sucedido, None caso contrário
    """
    try:
        # Tentar usar secrets do Streamlit primeiro (para produção)
        try:
            db_config = st.secrets["database"]
            connection_params = {
                'dbname': db_config["DB_NAME"],
                'user': db_config["DB_USER"],
                'password': db_config["DB_PASSWORD"],
                'host': db_config["DB_HOST"],
                'port': db_config["DB_PORT"]
            }
        except (KeyError, FileNotFoundError):
            # Fallback para arquivo secrets.toml local (para desenvolvimento)
            try:
                import toml
                
                if os.path.exists(".streamlit/secrets.toml"):
                    secrets = toml.load(".streamlit/secrets.toml")
                    
                    if "database" not in secrets:
                        raise KeyError("Seção 'database' não encontrada no secrets.toml")
                    
                    db_config = secrets["database"]
                    connection_params = {
                        'dbname': db_config["DB_NAME"],
                        'user': db_config["DB_USER"],
                        'password': db_config["DB_PASSWORD"],
                        'host': db_config["DB_HOST"],
                        'port': db_config["DB_PORT"]
                    }
                else:
                    st.error("❌ Credenciais do banco de dados não encontradas. Configure os secrets.")
                    return None
            except ImportError:
                st.error("❌ Biblioteca 'toml' não encontrada. Instale com: pip install toml")
                return None
            except Exception as toml_error:
                st.error(f"❌ Erro ao ler secrets.toml: {str(toml_error)}")
                return None
        
        # Tentar conectar ao banco
        connection = psycopg2.connect(**connection_params)
        connection.autocommit = True  # Para commits automáticos
        
        # Testar a conexão
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        return connection
        
    except psycopg2.Error as e:
        st.error(f"❌ Erro ao conectar ao banco de dados: {str(e)}")
        return None
    except Exception as e:
        st.error(f"❌ Erro ao configurar banco de dados:")
        st.error(f"📋 Detalhes: {str(e)}")
        st.error(f"🔧 Tipo do erro: {type(e).__name__}")
        return None

def enviar_para_banco_dados(dados_exportacao, consultor_selecionado):
    """
    Envia os dados do formulário para o banco de dados PostgreSQL
    Retorna o ID do envio para tracking
    """
    try:
        # Gerar ID único para este envio de formulário
        id_envio_form = str(uuid.uuid4())
        dados_exportacao["id_envio_form"] = id_envio_form
        
        # Configurar conexão
        connection = configurar_banco_dados()
        
        if connection is None:
            st.error("❌ Não foi possível conectar ao banco de dados")
            return None
        
        with connection.cursor() as cursor:
            # Inserir dados para cada cliente com resposta "Sim"
            for cliente_dados in dados_exportacao["clientes_sim"]:
                # Buscar o ID do cliente pelo nome
                select_sql = "SELECT id_cliente FROM cliente WHERE nome = %s"
                cursor.execute(select_sql, (cliente_dados["cliente"],))
                resultado = cursor.fetchone()
                
                if resultado is None:
                    st.warning(f"⚠️ Cliente '{cliente_dados['cliente']}' não encontrado na tabela cliente. Pulando...")
                    continue
                
                id_cliente = resultado[0]
                
                insert_sql = """
                INSERT INTO resposta_formularios 
                (data_resposta, id_cliente, enviar_relatorio, modulos, nota_consultor, id_envio_form, log_error_fluxo)
                VALUES (CURRENT_DATE, %s, %s, %s, %s, %s, %s)
                """
                
                modulos_str = ", ".join(cliente_dados["modulos"]) if cliente_dados["modulos"] else "Nenhum"
                
                cursor.execute(insert_sql, (
                    id_cliente,
                    True,  # enviar_relatorio = True
                    modulos_str,
                    cliente_dados["nota_consultor"] if cliente_dados["nota_consultor"] else "",
                    id_envio_form,
                    False  # log_error_fluxo = False inicialmente
                ))
            
            # Inserir dados para cada cliente com resposta "Não"
            for cliente_nao in dados_exportacao["clientes_nao"]:
                # Buscar o ID do cliente pelo nome
                select_sql = "SELECT id_cliente FROM cliente WHERE nome = %s"
                cursor.execute(select_sql, (cliente_nao,))
                resultado = cursor.fetchone()
                
                if resultado is None:
                    st.warning(f"⚠️ Cliente '{cliente_nao}' não encontrado na tabela cliente. Pulando...")
                    continue
                
                id_cliente = resultado[0]
                
                insert_sql = """
                INSERT INTO resposta_formularios 
                (data_resposta, id_cliente, enviar_relatorio, modulos, nota_consultor, id_envio_form, log_error_fluxo)
                VALUES (CURRENT_DATE, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(insert_sql, (
                    id_cliente,
                    False,  # enviar_relatorio = False
                    "",  # modulos vazio
                    "",   # nota_consultor vazio
                    id_envio_form,
                    False  # log_error_fluxo = False inicialmente
                ))
            
            # Confirmar transação
            connection.commit()
        
        return id_envio_form
        
    except psycopg2.Error as e:
        st.error(f"❌ Erro ao salvar no banco de dados: {str(e)}")
        if connection:
            connection.rollback()
        return None
    except Exception as e:
        st.error(f"❌ Erro inesperado ao salvar dados: {str(e)}")
        if connection:
            connection.rollback()
        return None
    finally:
        if connection:
            connection.close()

def verificar_status_envio(id_envio_form):
    """
    Verifica o status do envio no banco de dados
    Retorna: dict com informações do status
    """
    try:
        connection = configurar_banco_dados()
        if connection is None:
            return {"erro": "Não foi possível conectar ao banco de dados"}
        
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # Verificar status dos relatórios enviados
            status_sql = """
            SELECT 
                rf.id_cliente,
                c.nome as cliente_nome,
                rf.log_error_fluxo,
                rm.enviado,
                rf.modulos
            FROM resposta_formularios rf
            JOIN cliente c ON rf.id_cliente = c.id_cliente
            LEFT JOIN relatorio_mensal rm ON rf.id_cliente = rm.id_cliente 
                AND DATE(rm.data_de_envio) = CURRENT_DATE
            WHERE rf.id_envio_form = %s 
                AND rf.enviar_relatorio = true
            """
            
            cursor.execute(status_sql, (id_envio_form,))
            resultados = cursor.fetchall()
            
            if not resultados:
                return {"erro": "Nenhum registro encontrado para este envio"}
            
            status_clientes = []
            for resultado in resultados:
                # Garantir que sempre temos um nome de cliente
                nome_cliente = resultado['cliente_nome'] if resultado['cliente_nome'] else f"Cliente ID: {resultado['id_cliente']}"
                
                cliente_status = {
                    "cliente": nome_cliente,
                    "modulos": resultado['modulos'] if resultado['modulos'] else "Não especificado",
                    "erro_fluxo": bool(resultado['log_error_fluxo']),
                    "enviado": bool(resultado['enviado']) if resultado['enviado'] is not None else False,
                    "status": "processando"
                }
                
                # Determinar status final
                if resultado['log_error_fluxo']:
                    cliente_status["status"] = "erro"
                elif resultado['enviado']:
                    cliente_status["status"] = "sucesso"
                else:
                    cliente_status["status"] = "processando"
                
                status_clientes.append(cliente_status)
            
            return {"clientes": status_clientes}
        
    except Exception as e:
        return {"erro": f"Erro ao verificar status: {str(e)}"}
    finally:
        if connection:
            connection.close()

def monitorar_envios_com_timeout(id_envio_form, timeout_minutos=5):
    """
    Monitora os envios por um período determinado
    Retorna o status final após o timeout ou quando todos estiverem processados
    """
    timeout_segundos = timeout_minutos * 60
    inicio = time.time()
    
    # Log inicial para debug
    print(f"[DEBUG] Iniciando monitoramento para ID: {id_envio_form}")
    
    while (time.time() - inicio) < timeout_segundos:
        status = verificar_status_envio(id_envio_form)
        
        if "erro" in status:
            print(f"[DEBUG] Erro encontrado: {status['erro']}")
            return status
        
        # Verificar se todos os relatórios foram processados (sucesso ou erro)
        clientes = status.get("clientes", [])
        print(f"[DEBUG] Status atual - {len(clientes)} clientes encontrados")
        
        # Log do status de cada cliente para debug
        for cliente in clientes:
            print(f"[DEBUG] Cliente: {cliente.get('cliente', 'Nome não encontrado')} - Status: {cliente.get('status', 'Status não encontrado')}")
        
        todos_processados = all(
            cliente["status"] in ["sucesso", "erro"] 
            for cliente in clientes
        )
        
        if todos_processados:
            print(f"[DEBUG] Todos os relatórios foram processados")
            return status
        
        # Aguardar antes da próxima verificação
        time.sleep(10)  # Verificar a cada 10 segundos
    
    # Timeout atingido - retornar status atual e marcar timeouts
    status = verificar_status_envio(id_envio_form)
    if "clientes" in status:
        # Marcar clientes ainda processando como timeout
        for cliente in status["clientes"]:
            if cliente["status"] == "processando":
                cliente["status"] = "timeout"
                # Garantir que o nome do cliente esteja presente
                if not cliente.get("cliente"):
                    cliente["cliente"] = "Cliente não identificado"
    elif "erro" not in status:
        # Se não há clientes mas também não há erro, é um timeout geral
        return {"erro": "Timeout: Não foi possível verificar o status dos relatórios após 5 minutos"}
    
    return status

def configurar_google_sheets():
    """
    Configura a conexão com o Google Sheets
    Retorna (client, sheet_id) se bem-sucedido, (None, None) caso contrário
    """
    try:
        # Definir escopos necessários
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Tentar usar secrets do Streamlit primeiro (para produção)
        try:
            credentials_dict = st.secrets["api-google-drive"]
            sheet_id = st.secrets["google_sheet_id"]
            credentials = Credentials.from_service_account_info(
                credentials_dict, 
                scopes=scopes
            )
        except (KeyError, FileNotFoundError):
            # Fallback para arquivo secrets.toml local (para desenvolvimento)
            try:
                import toml
                
                # Tentar ler o arquivo secrets.toml
                if os.path.exists(".streamlit/secrets.toml"):
                    secrets = toml.load(".streamlit/secrets.toml")
                    
                    # Verificar se as chaves necessárias existem
                    if "api-google-drive" not in secrets:
                        raise KeyError("Seção 'api-google-drive' não encontrada no secrets.toml")
                    if "google_sheet_id" not in secrets:
                        raise KeyError("Campo 'google_sheet_id' não encontrado no secrets.toml")
                    
                    credentials_dict = secrets["api-google-drive"]
                    sheet_id = secrets["google_sheet_id"]  # Está no nível raiz do TOML
                    credentials = Credentials.from_service_account_info(
                        credentials_dict, 
                        scopes=scopes
                    )
                else:
                    # Último fallback para api-do-drive.json (compatibilidade)
                    if os.path.exists("api-do-drive.json"):
                        credentials = Credentials.from_service_account_file(
                            "api-do-drive.json", 
                            scopes=scopes
                        )
                        # Para desenvolvimento local com JSON, usar sheet_id padrão ou dos secrets
                        try:
                            sheet_id = st.secrets.get("google_sheet_id", "13jj-F3gBIkRoLPjT05x2A_JVXa6BlrXQWpvdRLVkmcw")
                        except:
                            sheet_id = "13jj-F3gBIkRoLPjT05x2A_JVXa6BlrXQWpvdRLVkmcw"
                    else:
                        st.error("❌ Credenciais não encontradas. Configure os secrets no Streamlit Cloud, adicione '.streamlit/secrets.toml' ou 'api-do-drive.json' localmente.")
                        return None, None
            except ImportError:
                st.error("❌ Biblioteca 'toml' não encontrada. Instale com: pip install toml")
                return None, None
            except Exception as toml_error:
                st.error(f"❌ Erro ao ler secrets.toml: {str(toml_error)}")
                # Fallback para api-do-drive.json se secrets.toml falhar
                if os.path.exists("api-do-drive.json"):
                    credentials = Credentials.from_service_account_file(
                        "api-do-drive.json", 
                        scopes=scopes
                    )
                    try:
                        sheet_id = st.secrets.get("google_sheet_id", "13jj-F3gBIkRoLPjT05x2A_JVXa6BlrXQWpvdRLVkmcw")
                    except:
                        sheet_id = "13jj-F3gBIkRoLPjT05x2A_JVXa6BlrXQWpvdRLVkmcw"
                else:
                    return None, None
        
        # Autorizar cliente
        client = gspread.authorize(credentials)
        
        # Testar conexão tentando acessar a planilha
        try:
            test_spreadsheet = client.open_by_key(sheet_id)
            test_worksheet = test_spreadsheet.worksheet("Respostas Formulário")
            # Se chegou até aqui, a conexão está funcionando
        except Exception as e:
            st.error(f"❌ Erro ao acessar a planilha: {str(e)}")
            st.error("🔍 Verifique se o ID da planilha está correto e se as permissões estão configuradas")
            return None, None
        
        return client, sheet_id
    except FileNotFoundError as e:
        st.error(f"❌ Arquivo de credenciais não encontrado: {e}")
        return None, None
    except json.JSONDecodeError as e:
        st.error(f"❌ Erro ao ler arquivo JSON de credenciais: {e}")
        st.error("🔍 Verifique se o arquivo de credenciais está com formato válido")
        return None, None
    except Exception as e:
        st.error(f"❌ Erro ao configurar Google Sheets:")
        st.error(f"📋 Detalhes: {str(e)}")
        st.error(f"🔧 Tipo do erro: {type(e).__name__}")
        return None, None

def enviar_para_google_sheets(dados_exportacao):
    """
    Envia os dados do formulário para o Google Sheets
    """
    try:
        # Configurar conexão
        client, sheet_id = configurar_google_sheets()
        
        if client is None or sheet_id is None:
            st.error("❌ Não foi possível conectar ao Google Sheets")
            return False
            
        # Abrir a planilha
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
    
    /* Estilo para status de envio */
    .status-container {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(255, 105, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid #FF6900;
    }
    
    .status-item-success {
        background: linear-gradient(135deg, #E8F5E8 0%, #D4F1D4 100%);
        border-left: 4px solid #66BB6A;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 8px;
    }
    
    .status-item-error {
        background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%);
        border-left: 4px solid #E57373;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 8px;
    }
    
    .status-item-timeout {
        background: linear-gradient(135deg, #FFF8E1 0%, #FFECB3 100%);
        border-left: 4px solid #FFB74D;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 8px;
    }
    
    .status-item-processing {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        border-left: 4px solid #42A5F5;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 8px;
    }
    
    /* Estilo para avisos sobre emojis */
    .emoji-warning {
        background-color: #FFF3CD !important;
        border: 1px solid #FFEAA7 !important;
        border-radius: 6px !important;
        padding: 8px !important;
        margin: 5px 0 !important;
        font-size: 0.85rem !important;
        color: #856404 !important;
    }
    
    /* Melhorar visibilidade dos text areas */
    .stTextArea > div > div > textarea {
        border: 2px solid #FFE5D6 !important;
        border-radius: 8px !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #FF6900 !important;
        box-shadow: 0 0 0 3px rgba(255, 105, 0, 0.1) !important;
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
    - ✅ A planilha tem o ID correto configurado nos secrets
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
            <li><strong>Selecione o seu nome</strong> na lista de consultores.</li>
            <li>Para cada cliente, <strong>indique</strong> se o relatório deve ser enviado.</li>
            <li><strong>Escolha os módulos</strong> e adicione observações, se necessário.</li>
            <li><strong>Envie</strong> o formulário ao finalizar.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

def formulario_principal():
    """
    Formulário principal que primeiro pede o consultor e depois mostra os clientes.
    """
    # Inicializar respostas na sessão
    if 'respostas_formulario' not in st.session_state:
        st.session_state.respostas_formulario = {}

    # Etapa 1: Seleção do Consultor
    lista_consultores = ["Selecione um consultor"] + sorted(list(CONSULTORES_CLIENTES.keys()))
    consultor_selecionado = st.selectbox(
        "👤 **Primeiro, selecione o consultor:**",
        options=lista_consultores,
        key="consultor_select"
    )

    respostas = {}
    
    # Etapa 2: Exibir o formulário para os clientes do consultor selecionado
    if consultor_selecionado != "Selecione um consultor":
        st.markdown(f"### Clientes de: {consultor_selecionado}")
        clientes_do_consultor = CONSULTORES_CLIENTES[consultor_selecionado]
        
        for cliente in clientes_do_consultor:
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
                        key=f"relatorio_{cliente}", # Chave única baseada no cliente
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
                        fc_check = st.checkbox("FC", key=f"fc_{cliente}")
                    with col_dre:
                        dre_check = st.checkbox("DRE", key=f"dre_{cliente}")
                    with col_ind:
                        ind_check = st.checkbox("Indicadores", key=f"ind_{cliente}")
                    
                    # Construir lista de módulos
                    if fc_check: modulos_selecionados.append("FC")
                    if dre_check: modulos_selecionados.append("DRE")
                    if ind_check: modulos_selecionados.append("Indicadores")
                    
                    # Campo de observações
                    nota_consultor = st.text_area(
                        "Nota do Consultor:",
                        placeholder="Digite aqui as suas observações adicionais para o relatório...",
                        height=80,
                        key=f"nota_{cliente}",
                        help="⚠️ Importante: Não utilize emojis nas notas do consultor. Eles serão automaticamente removidos."
                    )
                    
                    # Aviso visual sobre emojis
                    st.markdown("""
                    <div class="emoji-warning">
                        <strong>⚠️ Atenção:</strong> Não utilize emojis nas notas do consultor O sistema remove automaticamente caracteres especiais.
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Verificar se há emojis na nota e mostrar aviso
                    if nota_consultor:
                        nota_limpa = limpar_emojis_e_caracteres_especiais(nota_consultor)
                        if nota_consultor != nota_limpa:
                            st.warning(f"🧹 **Nota processada:** Emojis e caracteres especiais foram removidos automaticamente.")
                            if nota_limpa.strip():
                                st.info(f"📝 **Texto que será salvo:** \"{nota_limpa}\"")
                            else:
                                st.error("❌ **Atenção:** A nota ficou vazia após a remoção dos caracteres especiais.")
                    
                    # Validação
                    if not modulos_selecionados:
                        st.markdown('<div class="warning-message">Selecione pelo menos um módulo para gerar o relatório</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="success-message">Módulos selecionados: {", ".join(modulos_selecionados)}</div>', unsafe_allow_html=True)
                
                # Armazenar resposta (com limpeza da nota do consultor)
                nota_limpa = limpar_emojis_e_caracteres_especiais(nota_consultor) if nota_consultor else ""
                respostas[cliente] = {
                    "deseja_relatorio": deseja_relatorio,
                    "modulos": modulos_selecionados,
                    "nota_consultor": nota_limpa
                }
            
            st.markdown("<br>", unsafe_allow_html=True)
    
    return respostas

def processar_formulario_backend(respostas, consultor_selecionado):
    """
    Processa as respostas e envia os dados para o banco de dados PostgreSQL
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
            # Garantir que a nota do consultor esteja limpa antes de enviar
            nota_limpa = limpar_emojis_e_caracteres_especiais(dados["nota_consultor"]) if dados["nota_consultor"] else ""
            clientes_sim.append({
                "cliente": cliente,
                "modulos": dados["modulos"],
                "nota_consultor": nota_limpa
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
    
    # Enviar dados para o banco de dados PostgreSQL
    id_envio_form = enviar_para_banco_dados(dados_exportacao, consultor_selecionado)
    
    # Só retornar dados se o envio foi bem-sucedido
    if id_envio_form:
        dados_exportacao["id_envio_form"] = id_envio_form
        return dados_exportacao
    else:
        st.error("❌ Falha ao enviar os dados para o banco de dados. Tente novamente.")
        return None

def exibir_status_envio_realtime(id_envio_form, clientes_solicitados):
    """
    Exibe o status do envio em tempo real com monitoramento
    """
    st.markdown("---")
    st.markdown("### 📊 Status do Envio dos Relatórios")
    
    # Informações iniciais
    st.info(f"**Relatórios solicitados:** {len(clientes_solicitados)}")
    st.info("⏳ **Aguarde enquanto processamos seus relatórios. Isso pode levar até 5 minutos.**")
    
    # Container para o status que será atualizado
    status_placeholder = st.empty()
    
    with status_placeholder.container():
        # Progress bar inicial
        progress_bar = st.progress(0)
        
        # Iniciar monitoramento
        with st.spinner("🔄 Processando envio dos relatórios..."):
            status_final = monitorar_envios_com_timeout(id_envio_form, timeout_minutos=5)
            progress_bar.progress(100)
    
    # Limpar o placeholder e exibir resultados finais
    status_placeholder.empty()
    
    # Exibir resultados finais
    if "erro" in status_final:
        st.error(f"❌ **Erro no sistema:** {status_final['erro']}")
        st.markdown("🔧 **Entre em contato com a equipe de tecnologia:** [Clique aqui para abrir o WhatsApp](https://wa.me/556193691072)", unsafe_allow_html=True)
    else:
        clientes = status_final.get("clientes", [])
        
        if not clientes:
            st.warning("⚠️ Nenhum cliente encontrado para monitoramento.")
            return
        
        # Separar por status
        sucessos = [c for c in clientes if c["status"] == "sucesso"]
        erros = [c for c in clientes if c["status"] == "erro"]
        timeouts = [c for c in clientes if c["status"] == "timeout"]
        processando = [c for c in clientes if c["status"] == "processando"]
        
        # Estatísticas em destaque
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("✅ Enviados", len(sucessos), delta=f"{len(sucessos)}/{len(clientes)}")
        with col2:
            st.metric("❌ Erros", len(erros), delta="Falhas" if len(erros) > 0 else "Nenhuma")
        with col3:
            st.metric("⏰ Timeout", len(timeouts), delta="Aguardando" if len(timeouts) > 0 else "Completo")
        with col4:
            st.metric("🔄 Processando", len(processando), delta="Em andamento" if len(processando) > 0 else "Finalizado")
        
        # Detalhes por status
        if sucessos:
            st.success(f"✅ **{len(sucessos)} relatório(s) enviado(s) com sucesso:**")
            for cliente in sucessos:
                st.markdown(f"""
                <div class="status-item-success">
                    <strong>{cliente['cliente']}</strong><br>
                    📊 Módulos: {cliente['modulos']}<br>
                    ✅ Status: Enviado com sucesso
                </div>
                """, unsafe_allow_html=True)
        
        if erros:
            st.error(f"❌ **{len(erros)} relatório(s) com erro:**")
            for cliente in erros:
                st.markdown(f"""
                <div class="status-item-error">
                    <strong>{cliente['cliente']}</strong><br>
                    ❌ Erro ao enviar o relatório<br>
                    🔧 <strong>Ação:</strong> <a href="https://wa.me/556193691072" target="_blank">Clique aqui para contatar a equipe de tecnologia via WhatsApp</a>
                </div>
                """, unsafe_allow_html=True)
        
        if timeouts:
            st.error(f"⏰ **{len(timeouts)} relatório(s) com timeout:**")
            for cliente in timeouts:
                st.markdown(f"""
                <div class="status-item-error">
                    <strong>{cliente['cliente']}</strong><br>
                    ⏰ Timeout: O processamento demorou mais que 5 minutos<br>
                    <strong>Ação:</strong> <a href="https://wa.me/556193691072" target="_blank">Clique aqui para contatar a equipe de tecnologia via WhatsApp</a>
                </div>
                """, unsafe_allow_html=True)
        
        if processando:
            st.info(f"🔄 **{len(processando)} relatório(s) ainda em processamento:**")
            for cliente in processando:
                st.markdown(f"""
                <div class="status-item-processing">
                    <strong>{cliente['cliente']}</strong><br>
                    🔄 Ainda sendo processado<br>
                    ⏳ <strong>Status:</strong> Aguardando finalização
                </div>
                """, unsafe_allow_html=True)
        
        # Resumo final
        if len(sucessos) == len(clientes):
            st.balloons()
            st.success("🎉 **Todos os relatórios foram enviados com sucesso!**")
        elif len(erros) > 0 or len(timeouts) > 0:
            total_problemas = len(erros) + len(timeouts)
            st.error(f"⚠️ **{total_problemas} relatório(s) apresentaram problemas.**")
            st.markdown("🔧 **Entre em contato com a equipe de tecnologia:** [Clique aqui para abrir o WhatsApp](https://wa.me/556193691072)", unsafe_allow_html=True)
        elif len(processando) > 0:
            st.warning("⏳ **Alguns relatórios ainda estão sendo processados. Aguarde ou verifique novamente mais tarde.**")

def exibir_confirmacao_envio():
    """
    Exibe confirmação simples de envio com opção de novo formulário
    """
    st.markdown("---")
    
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
    
    # Só mostrar o botão de envio se houver respostas (ou seja, se um consultor foi selecionado)
    if respostas:
        st.markdown("---")    
        # Verificar se há respostas válidas
        respostas_validas = {k: v for k, v in respostas.items() if v["deseja_relatorio"] != "Selecione uma opção"}
        
        if not respostas_validas:
            st.warning("⚠️ Complete o formulário para pelo menos um cliente antes de enviar!")
        else:
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                if st.button("📤 Enviar Formulário", type="primary", use_container_width=True):
                    dados_exportacao = processar_formulario_backend(respostas, st.session_state.consultor_select)
                    if dados_exportacao:
                        st.session_state.dados_processados = dados_exportacao
                        # Força o rerun para mostrar o status de envio
                        st.rerun()

    # Mostrar status de envio se já foi processado
    if 'dados_processados' in st.session_state:
        dados_processados = st.session_state.dados_processados
        
        # Se há clientes com relatórios para enviar, mostrar status em tempo real
        if dados_processados.get("clientes_sim") and dados_processados.get("id_envio_form"):
            exibir_status_envio_realtime(
                dados_processados["id_envio_form"],
                dados_processados["clientes_sim"]
            )
        else:
            # Se não há relatórios para enviar, apenas mostrar confirmação simples
            st.success("✅ **Formulário processado com sucesso!**")
        
        # Botão para novo formulário
        exibir_confirmacao_envio()

if __name__ == "__main__":
    main()
