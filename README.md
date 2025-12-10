# Sistema de Análise de Sentimentos — MVP

envio de link da postagem e um fluxo de **análise mock** (pode plugar uma API real depois).

> **Stack**: Python 3.11+, FastAPI, SQLAlchemy, JWT, SQLite (dev), HTTPX (para chamadas a APIs), Uvicorn.

## Como rodar

1) Crie e ative um ambiente virtual (opcional mas é melhorr):
```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows: .venv\Scripts\activate
```

2) Instale dependências:
```bash
pip install -r requirements.txt #outra coisa, se o pyhton nao tiver atualizado, faz antesde rodar esse aqui
```

3) Defina variáveis de ambiente (dev):
```bash
export SECRET_KEY="dev-secret"                 # Windows (PowerShell): $Env:SECRET_KEY="dev-secret"
export ACCESS_TOKEN_EXPIRE_MINUTES="60"
export DATABASE_URL="sqlite:///./app.db"
```

4) Inicie o servidor:
```bash
uvicorn app.main:app --reload
```

Abra em: http://127.0.0.1:8000/docs (Swagger) ou /redoc.
# a porta vai depender da que voce for mudando, por ultimo eu usei a 8001 ent troquei

## Fluxo básico

- **POST /auth/register** → cria usuário (nome, sobrenome, e-mail, senha).
- **POST /auth/login** → retorna JWT.
- **POST /posts/analyze** (com Bearer token) → recebe `{ platform, url }`, cria uma "tarefa" de análise
  e executa **mock** de análise de sentimentos (positivo/negativo/neutral) em cima de comentários fictícios.
- **GET /analysis/{analysis_id}** → retorna resultado armazenado (agregados e comentários com rótulo).

> O módulo `app/services/sentiment.py` tem a **interface** `SentimentProvider`. Troque a classe `MockSentimentProvider`
por uma integração real (e.g., AWS Comprehend, Google Cloud Natural Language, Azure, Hugging Face, etc.).

## Estrutura

```
app/
  controller/        # pasta com os arquivos de requisições, chama serviços, retorna respostas ou views
    analysis.py      
    posts.py         
    users.py         
  model/             # pasta com os arquivos de estrutura de dados, conexão com banco, validações
    database.py      
    models.py        
    schemas.py       
  services/          # pasta com a lógica de negócio, autenticação, análise de sentimentos, etc
    auth.py            
    config.py        
    deps.py            
    sentiment.py
  view/              # pasta com a interface do projeto
    css/             # pasta com os arquivos de desing da interface do projeto
      styles.css
    html/            # pasta com os arquivos de interface html do projeto
      history.html
      login.html
      post.html
      register.html
      reset.html
      result.html
      save.html
    js/              # pasta com os arquivos de logica da interface do projeto
      app.js
  main.py            # arquivo de execução do projeto
```

## Próximos passos

  - Plugar um **provider real** de sentimento em `services/sentiment.py`.
  - Implementar coleta real de comentários por plataforma (API oficial quando possível).
  - Adicionar **testes** (pytest) e **migrations** (Alembic).
  - Substituir SQLite por Postgres em produção.
  - Criar um **frontend** (pode começar com HTML simples + fetch ao backend).

>- ESSE É UM FLUXO OPCIONAL, PODEM ALTERAR MAS AVISE AS MUDANÇAS NESSE READ ME PRO PROXIMO SABER 
- OS PROXIMOS PASSOS SAO IDEIAS DE UMA IA.


## Mudanças | Atualizações
```
* Para alteração de versão, seguir a seguinte logica:
  - Primeiro número: Mudanças grandes no projeto.
  - Segundo número: Adição de funcionalidades
  - Terceiro número: Correções pequenas ou bugs
```
  - v1.0.0 - Mudança na estrutura do projeto para uma estrutura MVC, desta forma melhorando a visualização e manutenções futuras.

  - v1.0.1 - Ajuste no arquivo app.js alterei a linha 41, estava "index" e alterei para "post" porque não estava encontrando o link

  - v1.1.0 - Adição de botões (navbar) para navegação entre as telas, pequenas mudanças na interface do sistema

  - v2.0.0 - Adição dos códigos de captura de comentários e analise de sentimento, e ajuste no register.html, pois não estava realizando o cadastro
  

## Redefinição de senha por e-mail

Endpoints:
- `POST /auth/reset-password` { "email": "user@dominio.com" }
- `POST /auth/reset-password-confirm` { "token": "...", "new_password": "..." }

Configurar SMTP por variáveis de ambiente:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=seuemail@gmail.com
SMTP_PASS=senha_ou_app_password
EMAIL_FROM=EmoSync <seuemail@gmail.com>
FRONTEND_BASE_URL=http://127.0.0.1:8000/frontend
```

## Banco de dados

Defina `DATABASE_URL` para usar um banco real:

- PostgreSQL:
  `DATABASE_URL=postgresql+psycopg2://usuario:senha@localhost:5432/emosync`

- MySQL:
  `DATABASE_URL=mysql+pymysql://usuario:senha@localhost:3306/emosync`

Se `DATABASE_URL` não for definido, usa `sqlite:///./app.db`.

Ao trocar para um banco novo, as tabelas são criadas automaticamente com as novas colunas (`reset_token`, `reset_token_expires`).
