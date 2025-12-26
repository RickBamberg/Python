from flask import Flask, render_template_string, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from datetime import datetime
import json

# Configuração do Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sistema.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

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
    column_list = ['id', 'nome', 'email', 'telefone', 'ativo', 'data_cadastro']
    column_searchable_list = ['nome', 'email', 'telefone']
    column_filters = ['nome', 'ativo', 'data_cadastro']
    column_editable_list = ['telefone', 'ativo']
    column_labels = {
        'nome': 'Nome Completo',
        'endereco': 'Endereço',
        'telefone': 'Telefone',
        'email': 'E-mail',
        'data_cadastro': 'Data de Cadastro',
        'ativo': 'Ativo'
    }
    form_columns = ['nome', 'email', 'telefone', 'endereco', 'ativo']
    column_default_sort = ('data_cadastro', True)
    column_formatters = {
        'data_cadastro': lambda v, c, m, p: m.data_cadastro.strftime('%d/%m/%Y %H:%M') if m.data_cadastro else ''
    }
    page_size = 20
    can_export = True
    export_types = ['csv', 'xlsx']


class UsuarioModelView(ModelView):
    column_list = ['id', 'username', 'nome_completo', 'email', 'cargo', 'ativo', 'data_criacao']
    column_searchable_list = ['username', 'nome_completo', 'email']
    column_filters = ['cargo', 'ativo', 'data_criacao']
    column_editable_list = ['cargo', 'ativo']
    column_labels = {
        'username': 'Usuário',
        'nome_completo': 'Nome Completo',
        'email': 'E-mail',
        'cargo': 'Cargo',
        'data_criacao': 'Data de Criação',
        'ativo': 'Ativo'
    }
    form_columns = ['username', 'nome_completo', 'email', 'cargo', 'ativo']
    column_default_sort = ('data_criacao', True)
    column_formatters = {
        'data_criacao': lambda v, c, m, p: m.data_criacao.strftime('%d/%m/%Y %H:%M') if m.data_criacao else ''
    }
    page_size = 20
    can_export = True
    export_types = ['csv', 'xlsx']


# ==================== VIEW CUSTOMIZADA: CALCULADORA ====================

class CalculadoraView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        resultado = None
        historico = []
        
        if request.method == 'POST':
            try:
                num1 = float(request.form.get('num1', 0))
                num2 = float(request.form.get('num2', 0))
                operacao = request.form.get('operacao')
                
                if operacao == 'soma':
                    resultado = num1 + num2
                    operacao_texto = '+'
                elif operacao == 'subtracao':
                    resultado = num1 - num2
                    operacao_texto = '-'
                elif operacao == 'multiplicacao':
                    resultado = num1 * num2
                    operacao_texto = '×'
                elif operacao == 'divisao':
                    if num2 != 0:
                        resultado = num1 / num2
                        operacao_texto = '÷'
                    else:
                        resultado = "Erro: Divisão por zero!"
                        operacao_texto = '÷'
                
                # Salvar no histórico (poderia ser no banco também)
                historico.append(f"{num1} {operacao_texto} {num2} = {resultado}")
                
            except ValueError:
                resultado = "Erro: Valores inválidos!"
        
        return self.render('admin/calculadora.html', resultado=resultado, historico=historico)


# ==================== VIEW CUSTOMIZADA: RELATÓRIOS ====================

class RelatoriosView(BaseView):
    @expose('/')
    def index(self):
        # Estatísticas dos clientes
        total_clientes = Cliente.query.count()
        clientes_ativos = Cliente.query.filter_by(ativo=True).count()
        clientes_inativos = total_clientes - clientes_ativos
        
        # Estatísticas dos usuários
        total_usuarios = Usuario.query.count()
        usuarios_ativos = Usuario.query.filter_by(ativo=True).count()
        
        # Clientes mais recentes
        ultimos_clientes = Cliente.query.order_by(Cliente.data_cadastro.desc()).limit(5).all()
        
        return self.render('admin/relatorios.html',
                         total_clientes=total_clientes,
                         clientes_ativos=clientes_ativos,
                         clientes_inativos=clientes_inativos,
                         total_usuarios=total_usuarios,
                         usuarios_ativos=usuarios_ativos,
                         ultimos_clientes=ultimos_clientes)


# ==================== VIEW CUSTOMIZADA: ENVIO DE EMAIL ====================

class EnviarEmailView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        mensagem = None
        clientes = Cliente.query.filter_by(ativo=True).all()
        
        if request.method == 'POST':
            destinatario = request.form.get('destinatario')
            assunto = request.form.get('assunto')
            corpo = request.form.get('corpo')
            
            # Aqui você colocaria a lógica real de envio de email
            # Por exemplo, usando flask-mail ou API de email
            mensagem = f"✅ Email enviado para {destinatario} com sucesso!"
            # Simulação: print(f"Enviando email para {destinatario}: {assunto}")
        
        return self.render('admin/enviar_email.html', 
                         mensagem=mensagem, 
                         clientes=clientes)


# ==================== CONFIGURAR FLASK-ADMIN ====================

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return True


admin = Admin(
    app,
    name='🏢 Sistema de Gestão',
    index_view=MyAdminIndexView(name='Dashboard', url='/admin')
)


# Adicionar views ao menu
admin.add_view(ClienteModelView(Cliente, db.session, name='Clientes', category='📋 Cadastros'))
admin.add_view(UsuarioModelView(Usuario, db.session, name='Usuários', category='📋 Cadastros'))

# Adicionar views customizadas
admin.add_view(CalculadoraView(name='Calculadora', endpoint='calculadora', category='🔧 Ferramentas'))
admin.add_view(RelatoriosView(name='Relatórios', endpoint='relatorios', category='📊 Análises'))
admin.add_view(EnviarEmailView(name='Enviar Email', endpoint='email', category='📧 Comunicação'))


# ==================== ROTAS NORMAIS DO FLASK ====================

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
            h1 { color: #2c3e50; margin-bottom: 20px; }
            .logo { font-size: 5em; margin-bottom: 20px; }
            a {
                display: inline-block;
                background-color: #667eea;
                color: white;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                transition: all 0.3s;
                margin: 10px;
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
            <a href="/admin">🚀 Painel Administrativo</a>
            <a href="/api/clientes">📡 API Clientes</a>
            <a href="/calcular/10/5">🧮 Calcular 10+5</a>
        </div>
    </body>
    </html>
    '''


# ==================== API REST ====================

@app.route('/api/clientes', methods=['GET'])
def api_clientes():
    """API que retorna todos os clientes em JSON"""
    clientes = Cliente.query.all()
    return jsonify([{
        'id': c.id,
        'nome': c.nome,
        'email': c.email,
        'telefone': c.telefone,
        'ativo': c.ativo
    } for c in clientes])


@app.route('/api/cliente/<int:id>', methods=['GET'])
def api_cliente(id):
    """API que retorna um cliente específico"""
    cliente = Cliente.query.get_or_404(id)
    return jsonify({
        'id': cliente.id,
        'nome': cliente.nome,
        'email': cliente.email,
        'telefone': cliente.telefone,
        'endereco': cliente.endereco,
        'ativo': cliente.ativo
    })


# ==================== ROTA DE CÁLCULO ====================

@app.route('/calcular/<float:num1>/<float:num2>')
def calcular(num1, num2):
    """Rota customizada que faz cálculos"""
    soma = num1 + num2
    subtracao = num1 - num2
    multiplicacao = num1 * num2
    divisao = num1 / num2 if num2 != 0 else 'Infinito'
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Resultado do Cálculo</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 50px;
            }}
            .result {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                max-width: 500px;
                margin: 0 auto;
            }}
            h2 {{ color: #667eea; }}
            .calc {{ font-size: 1.2em; margin: 10px 0; }}
            a {{ color: #667eea; text-decoration: none; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="result">
            <h2>🧮 Resultados dos Cálculos</h2>
            <div class="calc">➕ {num1} + {num2} = <strong>{soma}</strong></div>
            <div class="calc">➖ {num1} - {num2} = <strong>{subtracao}</strong></div>
            <div class="calc">✖️ {num1} × {num2} = <strong>{multiplicacao}</strong></div>
            <div class="calc">➗ {num1} ÷ {num2} = <strong>{divisao}</strong></div>
            <br>
            <a href="/">← Voltar</a> | <a href="/admin">Painel Admin</a>
        </div>
    </body>
    </html>
    """


# ==================== ROTA DE PROCESSAMENTO ====================

@app.route('/processar', methods=['GET', 'POST'])
def processar():
    """Exemplo de rota que processa dados"""
    if request.method == 'POST':
        dados = request.form.get('dados')
        # Aqui você pode fazer qualquer processamento
        resultado = dados.upper() if dados else ''
        return jsonify({'resultado': resultado, 'tamanho': len(resultado)})
    
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Processar Dados</title>
        <style>
            body { font-family: Arial; padding: 50px; background: #f5f5f5; }
            .container { background: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: 0 auto; }
            input[type="text"] { width: 100%; padding: 10px; margin: 10px 0; }
            button { background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Processar Dados</h2>
            <form method="POST">
                <input type="text" name="dados" placeholder="Digite algo aqui...">
                <button type="submit">Processar</button>
            </form>
        </div>
    </body>
    </html>
    """


# ==================== TEMPLATES CUSTOMIZADOS ====================

import os
os.makedirs('templates/admin', exist_ok=True)

# Template base customizado
custom_base = """
{% extends 'admin/base.html' %}
{% block head_css %}
{{ super() }}
<style>
    .navbar-brand { font-weight: bold; font-size: 1.5em; color: #2c3e50 !important; }
    .navbar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; }
    .navbar-nav .nav-link { color: white !important; }
    .sidebar { background-color: #f8f9fa; }
    .nav-item.active { background-color: #667eea; border-radius: 5px; }
    .btn-primary { background-color: #667eea; border-color: #667eea; }
    .btn-primary:hover { background-color: #764ba2; border-color: #764ba2; }
    .admin-logo { width: 40px; height: 40px; margin-right: 10px; border-radius: 50%; background-color: white; padding: 5px; }
    .dashboard-card { border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); padding: 20px; margin: 15px; background: white; }
    .card-icon { font-size: 3em; margin-bottom: 10px; }
</style>
{% endblock %}
{% block brand %}
<a class="navbar-brand" href="{{ admin_view.admin.url }}">
    <span class="admin-logo">🏢</span>
    {{ admin_view.admin.name }}
</a>
{% endblock %}
"""

# Template da calculadora
calculadora_template = """
{% extends 'admin/master.html' %}
{% block body %}
<div class="container-fluid">
    <h1 style="margin: 30px 0;">🧮 Calculadora</h1>
    
    <div class="row">
        <div class="col-md-6">
            <div class="card">
                <div class="card-body">
                    <form method="POST">
                        <div class="form-group">
                            <label>Número 1:</label>
                            <input type="number" step="any" name="num1" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label>Operação:</label>
                            <select name="operacao" class="form-control">
                                <option value="soma">➕ Soma</option>
                                <option value="subtracao">➖ Subtração</option>
                                <option value="multiplicacao">✖️ Multiplicação</option>
                                <option value="divisao">➗ Divisão</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Número 2:</label>
                            <input type="number" step="any" name="num2" class="form-control" required>
                        </div>
                        <button type="submit" class="btn btn-primary">Calcular</button>
                    </form>
                    
                    {% if resultado is not none %}
                    <div class="alert alert-success" style="margin-top: 20px;">
                        <h4>Resultado: {{ resultado }}</h4>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# Template de relatórios
relatorios_template = """
{% extends 'admin/master.html' %}
{% block body %}
<div class="container-fluid">
    <h1 style="margin: 30px 0;">📊 Relatórios e Estatísticas</h1>
    
    <div class="row">
        <div class="col-md-4">
            <div class="dashboard-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                <h3>👥 Clientes</h3>
                <h1>{{ total_clientes }}</h1>
                <p>✅ Ativos: {{ clientes_ativos }}</p>
                <p>❌ Inativos: {{ clientes_inativos }}</p>
            </div>
        </div>
        
        <div class="col-md-4">
            <div class="dashboard-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white;">
                <h3>🔐 Usuários</h3>
                <h1>{{ total_usuarios }}</h1>
                <p>✅ Ativos: {{ usuarios_ativos }}</p>
            </div>
        </div>
    </div>
    
    <div class="row" style="margin-top: 30px;">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header">
                    <h4>📋 Últimos Clientes Cadastrados</h4>
                </div>
                <div class="card-body">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Nome</th>
                                <th>Email</th>
                                <th>Telefone</th>
                                <th>Data de Cadastro</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for cliente in ultimos_clientes %}
                            <tr>
                                <td>{{ cliente.nome }}</td>
                                <td>{{ cliente.email }}</td>
                                <td>{{ cliente.telefone }}</td>
                                <td>{{ cliente.data_cadastro.strftime('%d/%m/%Y %H:%M') }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# Template de envio de email
email_template = """
{% extends 'admin/master.html' %}
{% block body %}
<div class="container-fluid">
    <h1 style="margin: 30px 0;">📧 Enviar Email para Clientes</h1>
    
    <div class="row">
        <div class="col-md-8">
            <div class="card">
                <div class="card-body">
                    {% if mensagem %}
                    <div class="alert alert-success">{{ mensagem }}</div>
                    {% endif %}
                    
                    <form method="POST">
                        <div class="form-group">
                            <label>Destinatário:</label>
                            <select name="destinatario" class="form-control" required>
                                <option value="">Selecione um cliente...</option>
                                {% for cliente in clientes %}
                                <option value="{{ cliente.email }}">{{ cliente.nome }} ({{ cliente.email }})</option>
                                {% endfor %}
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label>Assunto:</label>
                            <input type="text" name="assunto" class="form-control" required>
                        </div>
                        
                        <div class="form-group">
                            <label>Mensagem:</label>
                            <textarea name="corpo" class="form-control" rows="6" required></textarea>
                        </div>
                        
                        <button type="submit" class="btn btn-primary">📤 Enviar Email</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# Template dashboard customizado
custom_index = """
{% extends 'admin/master.html' %}
{% block body %}
<div class="container-fluid">
    <h1 style="margin: 30px 0; color: #2c3e50;">Bem-vindo ao Sistema de Gestão</h1>
    
    <div class="row">
        <div class="col-md-4">
            <div class="dashboard-card">
                <div class="card-icon" style="color: #667eea;">👥</div>
                <h3>Clientes</h3>
                <p>Gerencie seus clientes</p>
                <a href="{{ url_for('cliente.index_view') }}" class="btn btn-primary">Acessar</a>
            </div>
        </div>
        
        <div class="col-md-4">
            <div class="dashboard-card">
                <div class="card-icon" style="color: #764ba2;">🔐</div>
                <h3>Usuários</h3>
                <p>Administre usuários</p>
                <a href="{{ url_for('usuario.index_view') }}" class="btn btn-primary">Acessar</a>
            </div>
        </div>
        
        <div class="col-md-4">
            <div class="dashboard-card">
                <div class="card-icon" style="color: #f093fb;">🧮</div>
                <h3>Calculadora</h3>
                <p>Faça cálculos rápidos</p>
                <a href="{{ url_for('calculadora.index') }}" class="btn btn-primary">Acessar</a>
            </div>
        </div>
    </div>
    
    <div class="row" style="margin-top: 20px;">
        <div class="col-md-6">
            <div class="dashboard-card">
                <div class="card-icon" style="color: #667eea;">📊</div>
                <h3>Relatórios</h3>
                <p>Veja estatísticas detalhadas</p>
                <a href="{{ url_for('relatorios.index') }}" class="btn btn-primary">Acessar</a>
            </div>
        </div>
        
        <div class="col-md-6">
            <div class="dashboard-card">
                <div class="card-icon" style="color: #f5576c;">📧</div>
                <h3>Enviar Email</h3>
                <p>Comunique-se com clientes</p>
                <a href="{{ url_for('email.index') }}" class="btn btn-primary">Acessar</a>
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

with open('templates/admin/calculadora.html', 'w', encoding='utf-8') as f:
    f.write(calculadora_template)

with open('templates/admin/relatorios.html', 'w', encoding='utf-8') as f:
    f.write(relatorios_template)

with open('templates/admin/enviar_email.html', 'w', encoding='utf-8') as f:
    f.write(email_template)


# ==================== INICIALIZAR BANCO ====================

def inicializar_banco():
    with app.app_context():
        db.create_all()
        
        if Cliente.query.count() == 0:
            clientes_exemplo = [
                Cliente(nome='João Silva', endereco='Rua das Flores, 123', 
                       telefone='(11) 98765-4321', email='joao.silva@email.com', ativo=True),
                Cliente(nome='Maria Santos', endereco='Av. Principal, 456', 
                       telefone='(21) 91234-5678', email='maria.santos@email.com', ativo=True),
                Cliente(nome='Pedro Oliveira', endereco='Rua do Comércio, 789', 
                       telefone='(31) 99876-5432', email='pedro.oliveira@email.com', ativo=False)
            ]
            db.session.add_all(clientes_exemplo)
        
        if Usuario.query.count() == 0:
            usuarios_exemplo = [
                Usuario(username='admin', nome_completo='Administrador', 
                       email='admin@sistema.com', cargo='Administrador', ativo=True),
                Usuario(username='jsilva', nome_completo='João Silva', 
                       email='jsilva@sistema.com', cargo='Gerente', ativo=True),
                Usuario(username='msantos', nome_completo='Maria Santos', 
                       email='msantos@sistema.com', cargo='Operador', ativo=True)
            ]
            db.session.add_all(usuarios_exemplo)
        
        db.session.commit()
        print('✅ Banco inicializado!')


if __name__ == '__main__':
    inicializar_banco()
    print('🚀 Servidor: http://localhost:5000')
    print('📊 Admin: http://localhost:5000/admin')
    print('📡 API: http://localhost:5000/api/clientes')
    print('🧮 Cálculo: http://localhost:5000/calcular/10/5')
    app.run(debug=True)
