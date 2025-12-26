# API de Autenticação com Roles

> Projeto de exemplo em FastAPI que implementa autenticação com JWT (access + refresh tokens), controle de roles (admin, user, moderator) e armazenamento simples usando SQLite.

## Recursos

- Registro de usuários com hash de senha (bcrypt)
- Login com obtenção de `access_token` e `refresh_token`
- Renovação de `access_token` via `refresh_token`
- Logout (invalidação do `refresh_token`)
- Roles: `admin`, `user`, `moderator` com rotas protegidas para administradores
- Servir frontend estático em `static/index.html`

## Estrutura do projeto

- `main.py` - aplicação FastAPI principal
- `static/` - arquivos estáticos (ex.: `index.html`)
- `users.db` - banco SQLite (é criado automaticamente)

## Requisitos

- Python 3.9+
- Recomenda-se criar um ambiente virtual

Dependências principais (exemplo):

```bash
pip install fastapi uvicorn sqlalchemy pydantic passlib[bcrypt] python-jose[cryptography]
```

Você pode salvar as dependências em um `requirements.txt` com as linhas acima.

## Configuração

No arquivo `main.py` há variáveis configuráveis no topo:

- `SECRET_KEY` - chave secreta para tokens de acesso (mudar em produção)
- `REFRESH_SECRET_KEY` - (opcional) chave para refresh tokens (o código atual usa um token salvo no DB)
- `ALGORITHM` - algoritmo JWT (ex.: `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - validade do access token
- `REFRESH_TOKEN_EXPIRE_DAYS` - validade do refresh token

Em produção, NÃO deixe `SECRET_KEY` hard-coded; use variáveis de ambiente.

## Executando a aplicação

No terminal, na pasta do projeto, rode:

```bash
uvicorn main:app --reload
```

A API ficará disponível em `http://127.0.0.1:8000` e a documentação automática em `http://127.0.0.1:8000/docs`.

O endpoint raiz público também retorna informações de endpoints.

## Endpoints principais

- `POST /register` — Registrar novo usuário. Recebe JSON com `username`, `email`, `password`, `full_name` (opcional). Primeiro usuário criado vira `admin`.
- `POST /token` — Login (form data `username` e `password`). Retorna `access_token` e `refresh_token`.
- `POST /token/refresh` — Renovar `access_token` enviando `{ "refresh_token": "..." }`.
- `POST /logout` — Invalidar `refresh_token` (necessita usuário autenticado ativo e envio do `refresh_token`).
- `GET /users/me` — Dados do usuário autenticado (requer `Authorization: Bearer <access_token>`).
- `PUT /users/me` — Atualizar `full_name` e `email` do usuário autenticado.
- `GET /protected` — Exemplo de rota protegida para qualquer usuário autenticado.
- `GET /admin/users` — Listar todos os usuários (apenas `admin`).
- `PUT /admin/users/role` — Atualizar role de um usuário (apenas `admin`).
- `DELETE /admin/users/{user_id}` — Deletar usuário (apenas `admin`).
- `DELETE /admin/cleanup-tokens` — Remover refresh tokens expirados (apenas `admin`).

## Fluxo de autenticação (exemplos)

1) Registrar um usuário:

```bash
curl -X POST "http://127.0.0.1:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"senha123"}'
```

2) Obter tokens (login):

```bash
curl -X POST "http://127.0.0.1:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=senha123"
```

Resposta (exemplo):

```json
{
  "access_token": "<JWT_ACCESS>",
  "refresh_token": "<REFRESH_TOKEN>",
  "token_type": "bearer"
}
```

3) Acessar rota protegida com `access_token`:

```bash
curl -H "Authorization: Bearer <JWT_ACCESS>" http://127.0.0.1:8000/protected
```

4) Renovar `access_token` usando `refresh_token`:

```bash
curl -X POST "http://127.0.0.1:8000/token/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<REFRESH_TOKEN>"}'
```

## Observações de segurança

- Não exponha chaves secretas no repositório.
- Use HTTPS em produção.
- Considere armazenar tokens de refresh com mais metadados e implementar rotação de refresh tokens.

## Desenvolvimento e contribuições

- Sinta-se livre para abrir issues ou pull requests.
- Para testes rápidos, usar SQLite (já configurado no `main.py`).

## Licença

Coloque aqui a licença desejada (ex.: MIT) ou remova esta seção se preferir.

---

Arquivo principal: [main.py](main.py)
