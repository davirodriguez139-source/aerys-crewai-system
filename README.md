# AERYS CrewAI System

Sistema multiagente com CrewAI para gerar campanhas de marketing da AERYS (foco em execução via CLI e dashboard Streamlit).

---

### Estrutura do projeto

```text
aerys_crewai_system/
├── main.py
├── web_app.py
├── run_dashboard.sh
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── .streamlit/
│   └── secrets.toml.example
├── config/
├── data/                    # SQLite (auto-criado em runtime)
├── outputs/                 # Saídas .md geradas
└── src/
    ├── __init__.py
    ├── agents.py
    ├── tasks.py
    ├── crew.py
    ├── context_loader.py
    └── database.py
```

---

### Requisitos

- Python 3.10+
- Chave de API da Anthropic (`ANTHROPIC_API_KEY`)

Dependências principais (fixadas em versões mínimas estáveis em `requirements.txt`):

- `streamlit>=1.28.0`
- `crewai>=0.1.0`
- `crewai-tools>=0.1.0`
- `langchain-anthropic>=0.1.0`
- `anthropic>=0.7.0`
- `python-dotenv>=1.0.0`

---

### Setup local (desenvolvimento)

```bash
cd /home/ubuntu/aerys_crewai_system
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edite `.env` e configure:

```env
ANTHROPIC_API_KEY=your_real_key_here
```

Opcional:

```env
SERPER_API_KEY=your_serper_key_here
```

---

### Execução local (CLI)

```bash
python main.py
```

---

### Execução local (Streamlit)

```bash
streamlit run web_app.py
```

ou:

```bash
./run_dashboard.sh
```

URL local padrão:

```text
http://localhost:8501
```

> `web_app.py` usa fallback automático de configuração:
>
> 1. `st.secrets["ANTHROPIC_API_KEY"]` (Streamlit Cloud)
> 2. `.env` local (via `python-dotenv`)

---

### Deploy no Streamlit Cloud (passo a passo)

1. Suba este projeto para um repositório GitHub.
2. Acesse [https://share.streamlit.io](https://share.streamlit.io).
3. Clique em **New app**.
4. Selecione:
   - **Repository**: `seu-usuario/aerys-crewai-system`
   - **Branch**: `main` (ou branch de deploy)
   - **Main file path**: `web_app.py`
5. Abra **Advanced settings** → **Secrets**.
6. Cole as secrets no formato TOML abaixo:

```toml
ANTHROPIC_API_KEY = "sua-chave-real-aqui"
```

7. Clique em **Deploy**.

URL pública esperada:

```text
https://<nome-do-app>.streamlit.app
```

---

### Arquivo de exemplo para secrets

Existe um template em:

```text
.streamlit/secrets.toml.example
```

Conteúdo:

```toml
# Copy this file to secrets.toml and add your API key
ANTHROPIC_API_KEY = "your-api-key-here"
```

---

### Segurança e versionamento

O `.gitignore` foi configurado para **não versionar** dados sensíveis e artefatos locais, incluindo:

- `.env`
- `.streamlit/secrets.toml`
- `data/*.db`
- `outputs/*.md`
- cache Python e logs

---

### Troubleshooting

- **Erro: `ANTHROPIC_API_KEY is missing`**
  - Local: confirme se `.env` existe e possui a chave.
  - Streamlit Cloud: confirme se a chave está em **App Settings → Secrets**.

- **Falha na instalação de dependências**
  - Refaça deploy com as versões do `requirements.txt` atual.
  - Verifique se não há pacote extra conflitante no repositório.

- **App abre, mas não executa campanhas**
  - Confira logs no Streamlit Cloud.
  - Verifique se os arquivos de contexto em `/home/ubuntu/Uploads` foram adaptados para o ambiente de deploy (em produção, paths absolutos da VM local não existem).

---

### Observação importante sobre contexto

Atualmente o carregador de contexto (`src/context_loader.py`) lê arquivos markdown de um path absoluto local (`/home/ubuntu/Uploads`).

Para deploy em nuvem, recomenda-se mover esses arquivos para dentro do próprio repositório (ex.: `knowledge/`) e ajustar o loader para path relativo.
