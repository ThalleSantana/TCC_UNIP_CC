# Sistema de Análise de Sentimentos — MVP


envio de link da postagem e um fluxo de **análise mock** (pode plugar uma API real depois).

> **Stack**: Python 3.11+, FastAPI, SQLAlchemy, JWT, SQLite (dev), HTTPX (para chamadas a APIs), Uvicorn.

## Como rodar

1) Crie e ative um ambiente virtual (opcional mas é melhorr):
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
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
  main.py            # cria FastAPI e inclui rotas
  config.py          # configurações (SECRET_KEY, DB, etc.)
  database.py        # engine e SessionLocal
  models.py          # SQLAlchemy models (User, PostAnalysis, Comment)
  schemas.py         # Pydantic schemas
  auth.py            # utilitários de auth (hash, JWT)
  deps.py            # dependências (get_db, get_current_user)
  routers/
    users.py         # /auth/register e /auth/login
    posts.py         # /posts/analyze
    analysis.py      # /analysis/{id}
  services/
    sentiment.py     # provedor de sentimento (mock + interface)
```

## Próximos passos

  - Plugar um **provider real** de sentimento em `services/sentiment.py`.
  - Implementar coleta real de comentários por plataforma (API oficial quando possível).
  - Adicionar **testes** (pytest) e **migrations** (Alembic).
  - Substituir SQLite por Postgres em produção.
  - Criar um **frontend** (pode começar com HTML simples + fetch ao backend).

>- ESSE É UM FLUXO OPCIONAL, PODEM ALTERAR MAS AVISE AS MUDANÇAS NESSE READ ME PRO PROXIMO SABER 
- OS PROXIMOS PASSOS SAO IDEIAS DE UMA IA.
