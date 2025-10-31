# Automação de Relatórios Mensais

Sistema de formulário web desenvolvido com Streamlit para coletar e gerenciar dados sobre relatórios mensais de clientes. O sistema integra-se com Google Sheets e banco de dados PostgreSQL para armazenamento e análise dos dados.

## 📋 Descrição

Este projeto automatiza o processo de coleta de informações sobre relatórios mensais através de uma interface web intuitiva. Os consultores podem registrar dados sobre seus clientes, incluindo status de envio de relatórios, observações e outras informações relevantes.

### Funcionalidades Principais

- ✅ Interface web amigável para registro de relatórios
- 📊 Integração com Google Sheets para armazenamento de dados
- 🗄️ Suporte a banco de dados PostgreSQL
- 👥 Gerenciamento de consultores e seus respectivos clientes

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+**
- **Streamlit** - Framework para criação da interface web
- **Pandas** - Manipulação de dados
- **gspread** - Integração com Google Sheets
- **psycopg2** - Conexão com PostgreSQL
- **Google Auth** - Autenticação com Google APIs

## 📦 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git (opcional, para controle de versão)

## 🚀 Instalação e Configuração

### 1. Clone o Repositório (se aplicável)

```bash
git clone https://github.com/IZE-Gestao-Empresarial/Automacao_Relatorios_Mensais.git
cd Automacao_Relatorios_Mensais
```

### 2. Crie um Ambiente Virtual

É altamente recomendado usar um ambiente virtual para isolar as dependências do projeto.

#### No Windows (PowerShell)

```powershell
# Criar o ambiente virtual
python -m venv venv

# Ativar o ambiente virtual
.\venv\Scripts\Activate.ps1
```

#### No Windows (CMD)

```cmd
# Criar o ambiente virtual
python -m venv venv

# Ativar o ambiente virtual
venv\Scripts\activate.bat
```

#### No Linux/Mac

```bash
# Criar o ambiente virtual
python3 -m venv venv

# Ativar o ambiente virtual
source venv/bin/activate
```

> **Nota:** Após ativar o ambiente virtual, você verá `(venv)` no início da linha de comando, indicando que o ambiente está ativo.

### 3. Instale as Dependências

Com o ambiente virtual ativo, instale todas as dependências necessárias:

```bash
pip install -r requirements.txt
```

### 4. Configure as Credenciais

#### 4.1. Credenciais do Google Sheets

1. Crie um projeto no [Google Cloud Console](https://console.cloud.google.com/)
2. Ative a API do Google Sheets
3. Crie uma conta de serviço e baixe o arquivo JSON de credenciais
4. Crie a pasta `.streamlit` na raiz do projeto (se não existir)
5. Salve o arquivo de credenciais como `.streamlit/service_account.json`

#### 4.2. Configuração do Banco de Dados (Opcional)

Crie o arquivo `.streamlit/secrets.toml` com as seguintes informações:

```toml
[database]
DB_NAME = "seu_banco_de_dados"
DB_USER = "seu_usuario"
DB_PASSWORD = "sua_senha"
DB_HOST = "localhost"
DB_PORT = "5432"

[gcp_service_account]
# Cole aqui o conteúdo do seu arquivo service_account.json
```

> **⚠️ Importante:** Nunca compartilhe ou versione arquivos contendo credenciais sensíveis!

### 5. Estrutura de Diretórios

```
Automacao_Relatorios_Mensais/
│
├── .streamlit/
│   ├── secrets.toml              # Credenciais (não versionar)
│   └── service_account.json      # Credenciais Google (não versionar)
│
├── venv/                         # Ambiente virtual (não versionar)
│
├── formulario_relatorio_mensal.py  # Aplicação principal
├── requirements.txt              # Dependências do projeto
├── .gitignore                    # Arquivos ignorados pelo Git
└── README.md                     # Este arquivo
```

## ▶️ Como Executar o Projeto

### Com o Ambiente Virtual Ativo

1. **Certifique-se de que o ambiente virtual está ativo:**

   ```powershell
   # Windows PowerShell
   .\venv\Scripts\Activate.ps1
   ```

2. **Execute a aplicação Streamlit:**

   ```bash
   streamlit run formulario_relatorio_mensal.py
   ```

3. **Acesse a aplicação:**
   - O navegador abrirá automaticamente em `http://localhost:8501`
   - Caso não abra automaticamente, acesse manualmente o endereço exibido no terminal

### Parâmetros Adicionais

```bash
# Executar em uma porta específica
streamlit run formulario_relatorio_mensal.py --server.port 8502

# Executar sem abrir o navegador automaticamente
streamlit run formulario_relatorio_mensal.py --server.headless true
```

## 🔧 Comandos Úteis

### Gerenciamento do Ambiente Virtual

```powershell
# Ativar ambiente virtual (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Desativar ambiente virtual
deactivate

# Verificar pacotes instalados
pip list

# Atualizar requirements.txt (se adicionar novos pacotes)
pip freeze > requirements.txt
```

### Atualização de Dependências

```bash
# Atualizar um pacote específico
pip install --upgrade nome_do_pacote

# Atualizar todas as dependências
pip install --upgrade -r requirements.txt
```

## 📝 Uso da Aplicação

1. **Selecione o Consultor:** Escolha seu nome na lista de consultores
2. **Selecione o Cliente:** Escolha o cliente da lista associada ao consultor
3. **Preencha os Dados:** Complete as informações solicitadas no formulário
4. **Envie:** Clique no botão "Enviar" para registrar os dados

## 🐛 Solução de Problemas

### Erro ao Ativar o Ambiente Virtual (PowerShell)

Se receber erro de execução de scripts:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Erro de Conexão com Google Sheets

- Verifique se o arquivo `service_account.json` está na pasta `.streamlit`
- Confirme que a conta de serviço tem permissão no Google Sheet
- Verifique se a API do Google Sheets está ativada no projeto

### Erro de Conexão com Banco de Dados

- Verifique as credenciais no arquivo `secrets.toml`
- Confirme que o PostgreSQL está rodando
- Verifique as regras de firewall/conexão

## 📊 Dependências do Projeto

- `streamlit>=1.28.0` - Framework web
- `pandas>=1.5.0` - Análise de dados
- `gspread>=5.10.0` - Integração Google Sheets
- `google-auth>=2.20.0` - Autenticação Google
- `google-auth-oauthlib>=1.0.0` - OAuth Google
- `google-auth-httplib2>=0.1.0` - HTTP para Google Auth
- `toml>=0.10.2` - Parsing de arquivos TOML
- `psycopg2-binary>=2.9.0` - Driver PostgreSQL

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é propriedade da IZE Gestão Empresarial.

## 👥 Autores

**IZE Gestão Empresarial** - GitHub: [@IZE-Gestao-Empresarial](https://github.com/IZE-Gestao-Empresarial)

## 📞 Suporte

Para questões e suporte, entre em contato com a equipe de desenvolvimento da IZE Gestão Empresarial.

---
