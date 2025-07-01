from flask import Blueprint, request, jsonify, session
from src.database import db
from src.models.usuario import Usuario
from src.models.empresa import Empresa
from datetime import datetime

empresas_bp = Blueprint('empresas', __name__)

def require_auth():
    """Decorator para verificar autenticação"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    return None

def get_current_user():
    """Obter usuário atual da sessão"""
    if 'user_id' not in session:
        return None
    return Usuario.query.get(session['user_id'])

@empresas_bp.route('/empresas', methods=['GET'])
def listar_empresas():
    """Listar empresas baseado no perfil do usuário logado"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        usuario_atual = get_current_user()
        if not usuario_atual:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Super Admin pode ver todas as empresas
        if usuario_atual.perfil == 'super_admin':
            empresas = Empresa.query.all()
        # Admin do Cliente pode ver apenas sua empresa
        elif usuario_atual.perfil == 'admin_cliente':
            empresas = [usuario_atual.empresa] if usuario_atual.empresa else []
        else:
            return jsonify({'error': 'Acesso negado'}), 403
        
        return jsonify({
            'empresas': [empresa.to_dict() for empresa in empresas]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@empresas_bp.route('/empresas', methods=['POST'])
def criar_empresa():
    """Criar nova empresa (apenas Super Admin)"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        usuario_atual = get_current_user()
        if not usuario_atual:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Apenas Super Admin pode criar empresas
        if usuario_atual.perfil != 'super_admin':
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        
        # Validações básicas
        required_fields = ['nome', 'cnpj']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        nome = data['nome'].strip()
        cnpj = data['cnpj'].strip()
        
        # Verificar se CNPJ já existe
        if Empresa.query.filter_by(cnpj=cnpj).first():
            return jsonify({'error': 'CNPJ já cadastrado'}), 400
        
        # Criar nova empresa
        nova_empresa = Empresa(
            nome=nome,
            cnpj=cnpj,
            status=data.get('status', 'ativa'),
            logo_url=data.get('logo_url'),
            cores_personalizadas=data.get('cores_personalizadas')
        )
        
        db.session.add(nova_empresa)
        db.session.commit()
        
        return jsonify({
            'message': 'Empresa criada com sucesso',
            'empresa': nova_empresa.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@empresas_bp.route('/empresas/<int:empresa_id>', methods=['PUT'])
def atualizar_empresa(empresa_id):
    """Atualizar empresa existente"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        usuario_atual = get_current_user()
        if not usuario_atual:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        empresa = Empresa.query.get(empresa_id)
        if not empresa:
            return jsonify({'error': 'Empresa não encontrada'}), 404
        
        # Verificar permissões
        if usuario_atual.perfil == 'super_admin':
            # Super Admin pode editar qualquer empresa
            pass
        elif usuario_atual.perfil == 'admin_cliente':
            # Admin do Cliente só pode editar sua própria empresa
            if usuario_atual.empresa_id != empresa_id:
                return jsonify({'error': 'Acesso negado'}), 403
        else:
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        
        # Atualizar campos permitidos
        if 'nome' in data:
            empresa.nome = data['nome'].strip()
        
        if 'cnpj' in data and usuario_atual.perfil == 'super_admin':
            # Apenas Super Admin pode alterar CNPJ
            novo_cnpj = data['cnpj'].strip()
            if novo_cnpj != empresa.cnpj:
                # Verificar se novo CNPJ já existe
                if Empresa.query.filter_by(cnpj=novo_cnpj).first():
                    return jsonify({'error': 'CNPJ já cadastrado'}), 400
                empresa.cnpj = novo_cnpj
        
        if 'status' in data and usuario_atual.perfil == 'super_admin':
            # Apenas Super Admin pode alterar status
            empresa.status = data['status']
        
        if 'logo_url' in data:
            empresa.logo_url = data['logo_url']
        
        if 'cores_personalizadas' in data:
            empresa.cores_personalizadas = data['cores_personalizadas']
        
        empresa.data_atualizacao = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Empresa atualizada com sucesso',
            'empresa': empresa.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@empresas_bp.route('/empresas/<int:empresa_id>', methods=['DELETE'])
def deletar_empresa(empresa_id):
    """Desativar empresa (apenas Super Admin)"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        usuario_atual = get_current_user()
        if not usuario_atual:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Apenas Super Admin pode desativar empresas
        if usuario_atual.perfil != 'super_admin':
            return jsonify({'error': 'Acesso negado'}), 403
        
        empresa = Empresa.query.get(empresa_id)
        if not empresa:
            return jsonify({'error': 'Empresa não encontrada'}), 404
        
        empresa.status = 'inativa'
        empresa.data_atualizacao = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Empresa desativada com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@empresas_bp.route('/empresas/<int:empresa_id>/customizacao', methods=['GET'])
def obter_customizacao_empresa(empresa_id):
    """Obter configurações de customização da empresa"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        usuario_atual = get_current_user()
        if not usuario_atual:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        empresa = Empresa.query.get(empresa_id)
        if not empresa:
            return jsonify({'error': 'Empresa não encontrada'}), 404
        
        # Verificar se usuário pode acessar esta empresa
        if usuario_atual.perfil != 'super_admin' and usuario_atual.empresa_id != empresa_id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        return jsonify({
            'customizacao': {
                'logo_url': empresa.logo_url,
                'cores_personalizadas': empresa.cores_personalizadas or {}
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

