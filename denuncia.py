from src.database import db
from datetime import datetime
import uuid

class Denuncia(db.Model):
    __tablename__ = 'denuncias'
    
    id = db.Column(db.Integer, primary_key=True)
    protocolo = db.Column(db.String(20), unique=True, nullable=False)
    
    # Conteúdo da denúncia
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    subcategoria = db.Column(db.String(100))
    
    # Status e prioridade
    status = db.Column(db.String(20), default='recebida')  # recebida, em_analise, concluida, arquivada
    prioridade = db.Column(db.String(20), default='media')  # baixa, media, alta, critica
    
    # Relacionamentos
    anonima = db.Column(db.Boolean, default=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)  # Pode ser null se anônima
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    responsavel_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)  # Quem está analisando
    
    # Timestamps
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data_resolucao = db.Column(db.DateTime, nullable=True)
    
    # Metadados
    origem = db.Column(db.String(50), default='web')  # web, email, telefone
    ip_origem = db.Column(db.String(45))  # Para auditoria
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.protocolo:
            self.protocolo = self.gerar_protocolo()
    
    def gerar_protocolo(self):
        """Gera um protocolo único para a denúncia"""
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"DEN{timestamp}{unique_id}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'protocolo': self.protocolo,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'categoria': self.categoria,
            'subcategoria': self.subcategoria,
            'status': self.status,
            'prioridade': self.prioridade,
            'anonima': self.anonima,
            'usuario_id': self.usuario_id,
            'empresa_id': self.empresa_id,
            'responsavel_id': self.responsavel_id,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            'data_resolucao': self.data_resolucao.isoformat() if self.data_resolucao else None,
            'origem': self.origem,
            'ip_origem': self.ip_origem
        }

class HistoricoDenuncia(db.Model):
    __tablename__ = 'historico_denuncias'
    
    id = db.Column(db.Integer, primary_key=True)
    denuncia_id = db.Column(db.Integer, db.ForeignKey('denuncias.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    acao = db.Column(db.String(100), nullable=False)  # criada, atualizada, status_alterado, etc.
    descricao = db.Column(db.Text)
    status_anterior = db.Column(db.String(20))
    status_novo = db.Column(db.String(20))
    
    data_acao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'denuncia_id': self.denuncia_id,
            'usuario_id': self.usuario_id,
            'acao': self.acao,
            'descricao': self.descricao,
            'status_anterior': self.status_anterior,
            'status_novo': self.status_novo,
            'data_acao': self.data_acao.isoformat() if self.data_acao else None
        }

class CategoriasDenuncia(db.Model):
    __tablename__ = 'categorias_denuncia'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    ativa = db.Column(db.Boolean, default=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=True)  # Null = global
    
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'ativa': self.ativa,
            'empresa_id': self.empresa_id,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }

class SubcategoriasDenuncia(db.Model):
    __tablename__ = 'subcategorias_denuncia'
    
    id = db.Column(db.Integer, primary_key=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias_denuncia.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    ativa = db.Column(db.Boolean, default=True)
    
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'categoria_id': self.categoria_id,
            'nome': self.nome,
            'descricao': self.descricao,
            'ativa': self.ativa,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }

