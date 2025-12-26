from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from datetime import datetime

# Configuração do Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sistema.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'  # Tema de cores

# Inicializar banco de dados
db = SQLAlchemy(app)

# ==================== MODELOS ====================

class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.String(200))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True, nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Cliente {self.nome}>'


class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    nome_completo = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    cargo = db.Column(db.String(50))
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Usuario {self.username}>'


# ==================== VIEWS PERSONALIZADAS ====================

class ClienteModelView(ModelView):
    # Colunas exibidas na lista
    column_list = ['id', 'nome', 'email', 'telefone', 'ativo', 'data_cadastro']
    
    # Colunas pesquisáveis
    column_searchable_list = ['nome', 'email', 'telefone']
    
    # Filtros disponíveis
    column_filters = ['nome', 'ativo', 'data_cadastro']
    
    # Colunas editáveis inline
    column_editable_list = ['telefone', 'ativo']
    
    # Labels personalizados
    column_labels = {
        'nome': 'Nome Completo',
        'endereco': 'Endereço',
        'telefone': 'Telefone',
        'email': 'E-mail',
        'data_cadastro': 'Data de Cadastro',
        'ativo': 'Ativo'
    }
    
    # Configuração do formulário
    form_columns = ['nome', 'email', 'telefone', 'endereco', 'ativo']
    
    # Valores padrão
    column_default_sort = ('data_cadastro', True)
    
    # Formatação de data
    column_formatters = {
        'data_cadastro': lambda v, c, m, p: m.data_cadastro.strftime('%d/%m/%Y %H:%M') if m.data_cadastro else ''
    }
    
    # Paginação
    page_size = 20
    
    # Exportação
    can_export = True
    export_types = ['csv', 'xlsx']


class UsuarioModelView(ModelView):
    # Colunas exibidas na lista
    column_list = ['id', 'username', 'nome_completo', 'email', 'cargo', 'ativo', 'data_criacao']
    
    # Colunas pesquisáveis
    column_searchable_list = ['username', 'nome_completo', 'email']
    
    # Filtros disponíveis
    column_filters = ['cargo', 'ativo', 'data_criacao']
    
    # Colunas editáveis inline
    column_editable_list = ['cargo', 'ativo']
    
    # Labels personalizados
    column_labels = {
        'username': 'Usuário',
        'nome_completo': 'Nome Completo',
        'email': 'E-mail',
        'cargo': 'Cargo',
        'data_criacao': 'Data de Criação',
        'ativo': 'Ativo'
    }
    
    # Configuração do formulário
    form_columns = ['username', 'nome_completo', 'email', 'cargo', 'ativo']
    
    # Valores padrão
    column_default_sort = ('data_criacao', True)
    
    # Formatação de data
    column_formatters = {
        'data_criacao': lambda v, c, m, p: m.data_criacao.strftime('%d/%m/%Y %H:%M') if m.data_criacao else ''
    }
    
    # Paginação
    page_size = 20
    
    # Exportação
    can_export = True
    export_types = ['csv', 'xlsx']


# ==================== PÁGINA INICIAL CUSTOMIZADA ====================

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return True


# ==================== CONFIGURAR FLASK-ADMIN ====================

# Configuração SIMPLIFICADA para Flask-Admin 2.0.2
admin = Admin(
    app,
    name='🏢 Sistema de Gestão',
    index_view=MyAdminIndexView(name='Dashboard', url='/admin')
)

# Adicionar as views dos modelos ao menu
admin.add_view(ClienteModelView(Cliente, db.session, name='Clientes', category='📋 Cadastros'))
admin.add_view(UsuarioModelView(Usuario, db.session, name='Usuários', category='📋 Cadastros'))


# ==================== TEMPLATES CUSTOMIZADOS ====================

# Criar diretório de templates se não existir
import os
os.makedirs('templates/admin', exist_ok=True)

# Template base customizado
custom_base = """
{% extends 'admin/base.html' %}

{% block head_css %}
{{ super() }}
<style>
    /* Customização de cores */
    .navbar-brand {
        font-weight: bold;
        font-size: 1.5em;
        color: #2c3e50 !important;
    }
    
    .navbar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    .navbar-nav .nav-link {
        color: white !important;
    }
    
    .sidebar {
        background-color: #f8f9fa;
    }
    
    .nav-item.active {
        background-color: #667eea;
        border-radius: 5px;
    }
    
    .btn-primary {
        background-color: #667eea;
        border-color: #667eea;
    }
    
    .btn-primary:hover {
        background-color: #764ba2;
        border-color: #764ba2;
    }
    
    /* Logo */
    .admin-logo {
        width: 40px;
        height: 40px;
        margin-right: 10px;
        border-radius: 50%;
        background-color: white;
        padding: 5px;
    }
    
    /* Cards do dashboard */
    .dashboard-card {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        padding: 20px;
        margin: 15px;
        background: white;
    }
    
    .card-icon {
        font-size: 3em;
        margin-bottom: 10px;
    }
</style>
{% endblock %}

{% block brand %}
<a class="navbar-brand" href="{{ admin_view.admin.url }}">
    <span class="admin-logo">🏢</span>
    {{ admin_view.admin.name }}
</a>
{% endblock %}
"""

# Template da página inicial customizada
custom_index = """
{% extends 'admin/master.html' %}

{% block body %}
<div class="container-fluid">
    <h1 style="margin: 30px 0; color: #2c3e50;">Bem-vindo ao Sistema de Gestão</h1>
    
    <div class="row">
        <div class="col-md-6">
            <div class="dashboard-card">
                <div class="card-icon" style="color: #667eea;">👥</div>
                <h3>Clientes</h3>
                <p>Gerencie seus clientes de forma eficiente</p>
                <a href="{{ url_for('cliente.index_view') }}" class="btn btn-primary">Acessar Clientes</a>
            </div>
        </div>
        
        <div class="col-md-6">
            <div class="dashboard-card">
                <div class="card-icon" style="color: #764ba2;">🔐</div>
                <h3>Usuários</h3>
                <p>Administre os usuários do sistema</p>
                <a href="{{ url_for('usuario.index_view') }}" class="btn btn-primary">Acessar Usuários</a>
            </div>
        </div>
    </div>
    
    <div class="row" style="margin-top: 30px;">
        <div class="col-md-12">
            <div class="dashboard-card">
                <h4>📊 Recursos do Sistema</h4>
                <ul>
                    <li>✅ Cadastro completo de clientes e usuários</li>
                    <li>✅ Busca e filtros avançados</li>
                    <li>✅ Exportação para CSV e Excel</li>
                    <li>✅ Edição inline de dados</li>
                    <li>✅ Interface responsiva e moderna</li>
                </ul>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# Salvar templates
with open('templates/admin/custom_base.html', 'w', encoding='utf-8') as f:
    f.write(custom_base)

with open('templates/admin/custom_index.html', 'w', encoding='utf-8') as f:
    f.write(custom_index)


# ==================== ROTAS ====================

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema de Gestão</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 0;
            }
            .container {
                background: white;
                padding: 50px;
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                text-align: center;
            }
            h1 {
                color: #2c3e50;
                margin-bottom: 20px;
            }
            .logo {
                font-size: 5em;
                margin-bottom: 20px;
            }
            a {
                display: inline-block;
                background-color: #667eea;
                color: white;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                transition: all 0.3s;
            }
            a:hover {
                background-color: #764ba2;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🏢</div>
            <h1>Sistema de Gestão</h1>
            <p>Gerencie clientes e usuários de forma eficiente</p>
            <br>
            <a href="/admin">🚀 Acessar Painel Administrativo</a>
        </div>
    </body>
    </html>
    '''


# ==================== INICIALIZAR BANCO ====================

def inicializar_banco():
    with app.app_context():
        db.create_all()
        
        # Adicionar dados de exemplo se não existirem
        if Cliente.query.count() == 0:
            clientes_exemplo = [
                Cliente(
                    nome='João Silva',
                    endereco='Rua das Flores, 123 - São Paulo/SP',
                    telefone='(11) 98765-4321',
                    email='joao.silva@email.com',
                    ativo=True
                ),
                Cliente(
                    nome='Maria Santos',
                    endereco='Av. Principal, 456 - Rio de Janeiro/RJ',
                    telefone='(21) 91234-5678',
                    email='maria.santos@email.com',
                    ativo=True
                ),
                Cliente(
                    nome='Pedro Oliveira',
                    endereco='Rua do Comércio, 789 - Belo Horizonte/MG',
                    telefone='(31) 99876-5432',
                    email='pedro.oliveira@email.com',
                    ativo=False
                )
            ]
            db.session.add_all(clientes_exemplo)
        
        if Usuario.query.count() == 0:
            usuarios_exemplo = [
                Usuario(
                    username='admin',
                    nome_completo='Administrador do Sistema',
                    email='admin@sistema.com',
                    cargo='Administrador',
                    ativo=True
                ),
                Usuario(
                    username='jsilva',
                    nome_completo='João Silva',
                    email='jsilva@sistema.com',
                    cargo='Gerente',
                    ativo=True
                ),
                Usuario(
                    username='msantos',
                    nome_completo='Maria Santos',
                    email='msantos@sistema.com',
                    cargo='Operador',
                    ativo=True
                )
            ]
            db.session.add_all(usuarios_exemplo)
        
        db.session.commit()
        print('✅ Banco de dados inicializado com sucesso!')


if __name__ == '__main__':
    inicializar_banco()
    print('🚀 Servidor iniciado em http://localhost:5000')
    print('📊 Painel Admin em http://localhost:5000/admin')
    app.run(debug=True)
    