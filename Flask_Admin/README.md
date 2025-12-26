# Estudos com Flask-Admin

Este repositório contém vários exemplos e experimentos com Flask-Admin, organizados em pastas separadas (`Flask_Admin_1`, `Flask_Admin_2`, `Flask_Admin_3`, `Flask_Admin_4`). O objetivo foi estudar como integrar e customizar o Flask-Admin, testar múltiplas tabelas, menus e templates personalizados.

**Conteúdo do repositório**

- `Flask_Admin_1/`: Experimentos iniciais com uma app básica de Flask e primeiros testes do Flask-Admin.
- `Flask_Admin_2/`: Variação dos exemplos anteriores com pequenas alterações nas rotas e modelos.
- `Flask_Admin_3/`: Exemplo com templates personalizados para o painel administrativo. Contém `templates/admin/custom_base.html` e `templates/admin/custom_index.html` para demonstrar customização de layout do Flask-Admin.
- `Flask_Admin_4/`: Exemplo mais completo com várias páginas administrativas (por exemplo: `calculadora.html`, `enviar_email.html`, `relatorios.html`) e customizações adicionais em `templates/admin`.

**Estudos realizados**

- Integração básica do `Flask-Admin` com uma aplicação Flask.
- Customização do layout do admin usando templates Jinja2 (override de `base` e index do admin).
- Criação de múltiplos menus e views administrativas para diferentes modelos/tabelas.
- Testes de envio de e-mail a partir do app (ex.: páginas de envio de e-mail em `Flask_Admin_4`).
- Criação de páginas administrativas estáticas (relatórios, calculadora) integradas ao painel.

**Como executar os exemplos (Windows)**

1. Criar e ativar um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependências:

```powershell
pip install -r requirements.txt
```

3. Entrar na pasta do exemplo desejado e executar a app (cada pasta tem um `app.py`):

```powershell
cd Flask_Admin_4
python app.py
```

(Se os `app.py` estiverem configurados para executar com `flask run`, definir `FLASK_APP` antes.)

**Observações e sugestões**

- Dependências estão listadas em `requirements.txt`. Pode ser necessário ajustar versões conforme seu ambiente.
- Se os exemplos usam banco de dados (SQLite/SQLAlchemy), verifique se há arquivos de banco na pasta `instance/` ou configure as URIs apropriadas.
- Para aprofundar: adicionar exemplos com autenticação, permissões por usuário, e integração com APIs externas.

---
