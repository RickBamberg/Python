from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
app.config['SECRET_KEY'] = 'minha-chave-secreta-123'
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)

# Alternativa: sem template_mode
admin = Admin(app, name='Meu Admin')
admin.add_view(ModelView(Usuario, db.session))

@app.route('/')
def index():
    return '<a href="/admin/">Ir para o Admin</a>'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
