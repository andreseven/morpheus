from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class ConfiguracaoGlobal(db.Model):
    __tablename__ = 'configuracoes_globais'
    
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(100), unique=True, nullable=False)
    valor = db.Column(db.JSON)
    descricao = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'chave': self.chave,
            'valor': self.valor,
            'descricao': self.descricao,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }

class ConfiguracaoEmpresa(db.Model):
    __tablename__ = 'configuracoes_empresas'
    
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    chave = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.JSON)
    descricao = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Índice único para empresa_id + chave
    __table_args__ = (db.UniqueConstraint('empresa_id', 'chave', name='_empresa_chave_uc'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'empresa_id': self.empresa_id,
            'chave': self.chave,
            'valor': self.valor,
            'descricao': self.descricao,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }

class CategoriasDenuncia(db.Model):
    __tablename__ = 'categorias_denuncias'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    descricao = db.Column(db.Text)
    ativa = db.Column(db.Boolean, default=True)
    ordem = db.Column(db.Integer, default=0)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    subcategorias = db.relationship('SubcategoriasDenuncia', backref='categoria', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'ativa': self.ativa,
            'ordem': self.ordem,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'subcategorias': [sub.to_dict() for sub in self.subcategorias if sub.ativa]
        }

class SubcategoriasDenuncia(db.Model):
    __tablename__ = 'subcategorias_denuncias'
    
    id = db.Column(db.Integer, primary_key=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias_denuncias.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    ativa = db.Column(db.Boolean, default=True)
    ordem = db.Column(db.Integer, default=0)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'categoria_id': self.categoria_id,
            'nome': self.nome,
            'descricao': self.descricao,
            'ativa': self.ativa,
            'ordem': self.ordem,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }

