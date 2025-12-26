from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# Configuração do Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clientes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar banco de dados
db = SQLAlchemy(app)

# Modelo de Cliente
class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.String(200))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Cliente {self.nome}>'


# Personalizar a View do Cliente no Admin
class ClienteModelView(ModelView):
    # Colunas exibidas na lista
    column_list = ['id', 'nome', 'email', 'telefone', 'endereco']
    
    # Colunas pesquisáveis
    column_searchable_list = ['nome', 'email']
    
    # Filtros disponíveis
    column_filters = ['nome', 'email']
    
    # Colunas editáveis inline
    column_editable_list = ['telefone']
    
    # Labels personalizados
    column_labels = {
        'nome': 'Nome Completo',
        'endereco': 'Endereço',
        'telefone': 'Telefone',
        'email': 'E-mail'
    }
    
    # Configuração do formulário
    form_columns = ['nome', 'endereco', 'telefone', 'email']
    
    # Paginação
    page_size = 20


# Configurar Flask-Admin (SEM template_mode e base_template)
admin = Admin(app, name='Sistema de Clientes')

# Adicionar a view do modelo Cliente
admin.add_view(ClienteModelView(Cliente, db.session, name='Clientes'))


# Rota principal
@app.route('/')
def index():
    return '''
    <h1>Sistema de Gerenciamento de Clientes</h1>
    <p><a href="/admin">Acessar Painel Administrativo</a></p>
    '''


# Criar tabelas e dados de exemplo
def inicializar_banco():
    with app.app_context():
        db.create_all()
        
        # Verificar se já existem clientes
        if Cliente.query.count() == 0:
            # Adicionar clientes de exemplo
            clientes_exemplo = [
                Cliente(
                    nome='João Silva',
                    endereco='Rua das Flores, 123 - São Paulo/SP',
                    telefone='(11) 98765-4321',
                    email='joao.silva@email.com'
                ),
                Cliente(
                    nome='Maria Santos',
                    endereco='Av. Principal, 456 - Rio de Janeiro/RJ',
                    telefone='(21) 91234-5678',
                    email='maria.santos@email.com'
                ),
                Cliente(
                    nome='Pedro Oliveira',
                    endereco='Rua do Comércio, 789 - Belo Horizonte/MG',
                    telefone='(31) 99876-5432',
                    email='pedro.oliveira@email.com'
                )
            ]
            
            db.session.add_all(clientes_exemplo)
            db.session.commit()
            print('Banco de dados inicializado com clientes de exemplo!')


if __name__ == '__main__':
    inicializar_banco()
    app.run(debug=True)
