import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db, Usuario, Empresa, CategoriasDenuncia, SubcategoriasDenuncia
from src.main import app

def create_seed_data():
    """Criar dados de teste para o sistema"""
    
    with app.app_context():
        # Limpar dados existentes
        db.drop_all()
        db.create_all()
        
        # Criar empresas
        empresa1 = Empresa(
            nome="TechCorp Ltda",
            cnpj="12.345.678/0001-90",
            status="ativa",
            cores_personalizadas={
                "primary": "#1e40af",
                "secondary": "#64748b"
            }
        )
        
        empresa2 = Empresa(
            nome="InnovaSoft S.A.",
            cnpj="98.765.432/0001-10",
            status="ativa",
            cores_personalizadas={
                "primary": "#059669",
                "secondary": "#374151"
            }
        )
        
        db.session.add(empresa1)
        db.session.add(empresa2)
        db.session.commit()
        
        # Criar usuários
        # Super Admin
        super_admin = Usuario(
            email="admin@morpheus.com",
            nome="Administrador do Sistema",
            perfil="super_admin"
        )
        super_admin.set_senha("admin123")
        
        # Admin Cliente - TechCorp
        admin_techcorp = Usuario(
            email="admin@techcorp.com",
            nome="João Silva",
            perfil="admin_cliente",
            empresa_id=empresa1.id
        )
        admin_techcorp.set_senha("admin123")
        
        # Admin Cliente - InnovaSoft
        admin_innovasoft = Usuario(
            email="admin@innovasoft.com",
            nome="Maria Santos",
            perfil="admin_cliente",
            empresa_id=empresa2.id
        )
        admin_innovasoft.set_senha("admin123")
        
        # Auditoria - TechCorp
        auditoria_techcorp = Usuario(
            email="auditoria@techcorp.com",
            nome="Carlos Oliveira",
            perfil="auditoria",
            empresa_id=empresa1.id
        )
        auditoria_techcorp.set_senha("audit123")
        
        # Gerente - TechCorp
        gerente_techcorp = Usuario(
            email="gerente@techcorp.com",
            nome="Ana Costa",
            perfil="gerente",
            empresa_id=empresa1.id
        )
        gerente_techcorp.set_senha("gerente123")
        
        # Cliente - TechCorp
        cliente_techcorp = Usuario(
            email="cliente@techcorp.com",
            nome="Pedro Almeida",
            perfil="cliente",
            empresa_id=empresa1.id
        )
        cliente_techcorp.set_senha("cliente123")
        
        db.session.add_all([
            super_admin, admin_techcorp, admin_innovasoft,
            auditoria_techcorp, gerente_techcorp, cliente_techcorp
        ])
        
        # Criar categorias de denúncias
        cat_seguranca = CategoriasDenuncia(
            nome="Segurança da Informação",
            descricao="Questões relacionadas à segurança de dados e informações",
            ordem=1
        )
        
        cat_fraudes = CategoriasDenuncia(
            nome="Fraudes e Integridade Corporativa",
            descricao="Denúncias sobre fraudes, corrupção e integridade",
            ordem=2
        )
        
        cat_conduta = CategoriasDenuncia(
            nome="Conduta, Compliance e Recursos Humanos",
            descricao="Questões de conduta ética e recursos humanos",
            ordem=3
        )
        
        db.session.add_all([cat_seguranca, cat_fraudes, cat_conduta])
        db.session.commit()
        
        # Criar subcategorias
        subcategorias_seguranca = [
            "Acesso à informação",
            "Dados Pessoais - LGPD",
            "Governança Digital",
            "Normas e Fiscalização",
            "Redes Sociais",
            "Transparência",
            "Auditoria",
            "Controle social",
            "Ouvidoria Interna"
        ]
        
        subcategorias_fraudes = [
            "Corrupção",
            "Denúncia Crime",
            "Denúncia de irregularidades",
            "Lavagem de dinheiro",
            "Sistema Financeiro",
            "Licitações",
            "Benefício",
            "Cadastro",
            "Certidões e Declarações",
            "Propriedade Industrial",
            "Seguro",
            "Operações"
        ]
        
        subcategorias_conduta = [
            "Assédio moral",
            "Assédio sexual",
            "Discriminação",
            "Conduta Ética",
            "Racismo",
            "Recursos Humanos",
            "Frequência de Servidores",
            "Relações de Trabalho"
        ]
        
        # Adicionar subcategorias de segurança
        for i, nome in enumerate(subcategorias_seguranca):
            sub = SubcategoriasDenuncia(
                categoria_id=cat_seguranca.id,
                nome=nome,
                ordem=i+1
            )
            db.session.add(sub)
        
        # Adicionar subcategorias de fraudes
        for i, nome in enumerate(subcategorias_fraudes):
            sub = SubcategoriasDenuncia(
                categoria_id=cat_fraudes.id,
                nome=nome,
                ordem=i+1
            )
            db.session.add(sub)
        
        # Adicionar subcategorias de conduta
        for i, nome in enumerate(subcategorias_conduta):
            sub = SubcategoriasDenuncia(
                categoria_id=cat_conduta.id,
                nome=nome,
                ordem=i+1
            )
            db.session.add(sub)
        
        db.session.commit()
        
        print("Dados de teste criados com sucesso!")
        print("\nUsuários criados:")
        print("Super Admin: admin@morpheus.com / admin123")
        print("Admin TechCorp: admin@techcorp.com / admin123")
        print("Admin InnovaSoft: admin@innovasoft.com / admin123")
        print("Auditoria TechCorp: auditoria@techcorp.com / audit123")
        print("Gerente TechCorp: gerente@techcorp.com / gerente123")
        print("Cliente TechCorp: cliente@techcorp.com / cliente123")

if __name__ == "__main__":
    create_seed_data()

