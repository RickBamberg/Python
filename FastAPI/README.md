# FastAPI Project

Projeto FastAPI simples com rotas de autenticação e gerenciamento de pedidos, usando Alembic para migrações.

## Visão geral

- Aplicação construída com FastAPI.
- Rotas principais implementadas em [auth_routes.py](auth_routes.py) e [order_routes.py](order_routes.py).
- Modelos e schemas em [models.py](models.py) e [schemas.py](schemas.py).
- Migrações gerenciadas com Alembic (pasta `alembic/`).

## Estrutura principal

- [main.py](main.py) — ponto de entrada da aplicação.
- [auth_routes.py](auth_routes.py) — endpoints de autenticação.
- [order_routes.py](order_routes.py) — endpoints relacionados a pedidos.
- [models.py](models.py) — modelos SQLAlchemy.
- [schemas.py](schemas.py) — Pydantic schemas.
- [alembic/](alembic/) — migrações do banco de dados.

## Requisitos

- Python 3.9+
- Dependências listadas em `requirements.txt`.

## Instalação

1. Crie e ative um virtualenv (recomendado):

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# PowerShell
. .venv\Scripts\Activate.ps1
```

2. Instale dependências:

```bash
pip install -r requirements.txt
```

3. Configure variáveis de ambiente (exemplos):

- `DATABASE_URL` — URL de conexão com o banco (Postgres, SQLite, etc.).
- `SECRET_KEY` — chave para assinatura de tokens.
- `ACCESS_TOKEN_EXPIRE_MINUTES` — tempo de expiração do token.

Você pode usar um arquivo `.env` e um loader (por exemplo `python-dotenv`) se preferir.

## Migrações (Alembic)

Gerar e aplicar migrações:

```bash
alembic revision --autogenerate -m "mensagem"
alembic upgrade head
```

As versões de migração ficam em `alembic/versions/`.

## Executando a aplicação

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

A documentação automática do FastAPI estará disponível em `http://localhost:8000/docs`.

## Endpoints (visão geral)

Consulte os arquivos de rota para detalhes dos endpoints. Exemplos comuns:

- Autenticação: rotas agrupadas em [auth_routes.py](auth_routes.py) — endpoints como `POST /auth/login` e `POST /auth/register`.
- Pedidos: rotas agrupadas em [order_routes.py](order_routes.py) — operações CRUD para pedidos.

Exemplo de login (curl):

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"senha"}'
```

Exemplo de requisição autenticada:

```bash
curl "http://localhost:8000/orders" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

(Ajuste URLs e payloads conforme o que está implementado em `auth_routes.py` e `order_routes.py`.)

## Testes

Nenhum teste automatizado incluído por padrão. Adicione `pytest` e escreva testes em `tests/` se desejar.

## Contribuindo

1. Crie uma branch para sua feature: `git checkout -b feature/minha-feature`.
2. Faça commits pequenos e claros.
3. Abra um pull request descrevendo as mudanças.

## Licença

Escolha uma licença para o projeto (ex.: MIT). Selecione e adicione um arquivo `LICENSE`.

---
