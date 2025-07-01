from src.database import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    nome = db.Column(db.String(255), nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(50), nullable=False)  # super_admin, admin_cliente, auditoria, gerente, cliente
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=True)
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime)
    
    def set_senha(self, senha):
        """Define a senha do usuário (hash)"""
        self.senha_hash = generate_password_hash(senha)
    
    def check_senha(self, senha):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, senha)
    
    def can_view_denuncia(self, denuncia):
        """Verificar se o usuário pode visualizar uma denúncia específica"""
        if self.perfil == 'super_admin':
            return True
        elif self.perfil in ['admin_cliente', 'auditoria', 'gerente']:
            return denuncia.empresa_id == self.empresa_id
        elif self.perfil == 'cliente':
            return denuncia.usuario_id == self.id or denuncia.anonima
        return False
    
    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'email': self.email,
            'nome': self.nome,
            'perfil': self.perfil,
            'empresa_id': self.empresa_id,
            'ativo': self.ativo,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'ultimo_login': self.ultimo_login.isoformat() if self.ultimo_login else None
        }
        
        if include_sensitive:
            data['senha_hash'] = self.senha_hash
            
        return data

