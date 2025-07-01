import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.database import db
from src.models.usuario import Usuario
from src.models.empresa import Empresa
from src.models.denuncia import Denuncia, CategoriasDenuncia, SubcategoriasDenuncia
from werkzeug.security import generate_password_hash
from datetime import datetime

def seed_data():
    """Inserir dados de teste no banco de dados"""
    with app.app_context():
        # Criar empresa
        empresa = Empresa(
            nome="Morpheus Corp",
            cnpj="12.345.678/0001-90"
        )
        db.session.add(empresa)
        db.session.commit()
        
        # Criar usuário admin
        admin = Usuario(
            nome="Administrador do Sistema",
            email="admin@morpheus.com",
            senha_hash=generate_password_hash("admin123"),
            perfil="super_admin",
            empresa_id=empresa.id,
            ativo=True
        )
        db.session.add(admin)
        db.session.commit()
        
        # Criar categorias
        categorias = [
            {"nome": "Segurança da Informação", "descricao": "Denúncias relacionadas à segurança de dados e informações"},
            {"nome": "Fraudes e Integridade Corporativa", "descricao": "Denúncias sobre fraudes, corrupção e questões de integridade"},
            {"nome": "Conduta, Compliance e Recursos Humanos", "descricao": "Denúncias sobre conduta inadequada, assédio e questões de RH"}
        ]
        
        for cat_data in categorias:
            categoria = CategoriasDenuncia(**cat_data)
            db.session.add(categoria)
        
        db.session.commit()
        
        # Criar denúncias de teste
        denuncias = [
            {
                "titulo": "Vazamento de dados confidenciais",
                "descricao": "Funcionário compartilhando informações confidenciais com terceiros",
                "categoria": "Segurança da Informação",
                "subcategoria": "Vazamento de dados",
                "status": "recebida",
                "prioridade": "alta",
                "empresa_id": empresa.id,
                "anonima": True
            },
            {
                "titulo": "Suspeita de fraude em licitação",
                "descricao": "Possível manipulação de processo licitatório",
                "categoria": "Fraudes e Integridade Corporativa", 
                "subcategoria": "Fraude em processos",
                "status": "em_analise",
                "prioridade": "critica",
                "empresa_id": empresa.id,
                "usuario_id": admin.id,
                "anonima": False
            },
            {
                "titulo": "Assédio moral no departamento",
                "descricao": "Relatos de assédio moral por parte de supervisor",
                "categoria": "Conduta, Compliance e Recursos Humanos",
                "subcategoria": "Assédio moral",
                "status": "em_analise",
                "prioridade": "alta",
                "empresa_id": empresa.id,
                "anonima": True
            },
            {
                "titulo": "Uso inadequado de recursos da empresa",
                "descricao": "Funcionário utilizando recursos da empresa para fins pessoais",
                "categoria": "Fraudes e Integridade Corporativa",
                "subcategoria": "Uso inadequado de recursos",
                "status": "concluida",
                "prioridade": "media",
                "empresa_id": empresa.id,
                "usuario_id": admin.id,
                "anonima": False,
                "data_resolucao": datetime.utcnow()
            },
            {
                "titulo": "Acesso não autorizado a sistemas",
                "descricao": "Tentativas de acesso não autorizado aos sistemas internos",
                "categoria": "Segurança da Informação",
                "subcategoria": "Acesso não autorizado",
                "status": "recebida",
                "prioridade": "alta",
                "empresa_id": empresa.id,
                "anonima": True
            }
        ]
        
        for den_data in denuncias:
            denuncia = Denuncia(**den_data)
            db.session.add(denuncia)
        
        db.session.commit()
        print("Dados de teste inseridos com sucesso!")

if __name__ == "__main__":
    seed_data()

