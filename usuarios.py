from flask import Blueprint, request, jsonify, session
from src.database import db
from src.models.usuario import Usuario
from src.models.empresa import Empresa
from datetime import datetime

usuarios_bp = Blueprint('usuarios', __name__)

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

@usuarios_bp.route('/usuarios', methods=['GET'])
def listar_usuarios():
    """Listar usuários baseado no perfil do usuário logado"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        usuario_atual = get_current_user()
        if not usuario_atual:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Super Admin pode ver todos os usuários
        if usuario_atual.perfil == 'super_admin':
            usuarios = Usuario.query.all()
        # Admin do Cliente pode ver usuários de sua empresa
        elif usuario_atual.perfil == 'admin_cliente':
            usuarios = Usuario.query.filter_by(empresa_id=usuario_atual.empresa_id).all()
        else:
            return jsonify({'error': 'Acesso negado'}), 403
        
        return jsonify({
            'usuarios': [usuario.to_dict() for usuario in usuarios]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@usuarios_bp.route('/usuarios', methods=['POST'])
def criar_usuario():
    """Criar novo usuário"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        usuario_atual = get_current_user()
        if not usuario_atual:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        
        # Validações básicas
        required_fields = ['email', 'nome', 'senha', 'perfil']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        email = data['email'].lower().strip()
        nome = data['nome'].strip()
        senha = data['senha']
        perfil = data['perfil']
        empresa_id = data.get('empresa_id')
        
        # Verificar se email já existe
        if Usuario.query.filter_by(email=email).first():
            return jsonify({'error': 'Email já cadastrado'}), 400
        
        # Verificar permissões
        if usuario_atual.perfil == 'super_admin':
            # Super Admin pode criar qualquer tipo de usuário
            if perfil == 'super_admin':
                empresa_id = None
            elif empresa_id:
                empresa = Empresa.query.get(empresa_id)
                if not empresa:
                    return jsonify({'error': 'Empresa não encontrada'}), 404
        elif usuario_atual.perfil == 'admin_cliente':
            # Admin do Cliente só pode criar usuários de sua empresa
            if perfil in ['super_admin', 'admin_cliente']:
                return jsonify({'error': 'Acesso negado para criar este tipo de usuário'}), 403
            empresa_id = usuario_atual.empresa_id
        else:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Criar novo usuário
        novo_usuario = Usuario(
            email=email,
            nome=nome,
            perfil=perfil,
            empresa_id=empresa_id
        )
        novo_usuario.set_senha(senha)
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'usuario': novo_usuario.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@usuarios_bp.route('/usuarios/<int:usuario_id>', methods=['PUT'])
def atualizar_usuario(usuario_id):
    """Atualizar usuário existente"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        usuario_atual = get_current_user()
        if not usuario_atual:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Verificar permissões
        if usuario_atual.perfil == 'super_admin':
            # Super Admin pode editar qualquer usuário
            pass
        elif usuario_atual.perfil == 'admin_cliente':
            # Admin do Cliente só pode editar usuários de sua empresa
            if usuario.empresa_id != usuario_atual.empresa_id:
                return jsonify({'error': 'Acesso negado'}), 403
            # Não pode editar Super Admin ou Admin de outras empresas
            if usuario.perfil in ['super_admin', 'admin_cliente'] and usuario.id != usuario_atual.id:
                return jsonify({'error': 'Acesso negado'}), 403
        else:
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        
        # Atualizar campos permitidos
        if 'nome' in data:
            usuario.nome = data['nome'].strip()
        
        if 'email' in data:
            novo_email = data['email'].lower().strip()
            if novo_email != usuario.email:
                # Verificar se novo email já existe
                if Usuario.query.filter_by(email=novo_email).first():
                    return jsonify({'error': 'Email já cadastrado'}), 400
                usuario.email = novo_email
        
        if 'perfil' in data and usuario_atual.perfil == 'super_admin':
            # Apenas Super Admin pode alterar perfis
            usuario.perfil = data['perfil']
        
        if 'ativo' in data:
            usuario.ativo = data['ativo']
        
        if 'senha' in data and data['senha']:
            usuario.set_senha(data['senha'])
        
        usuario.data_atualizacao = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Usuário atualizado com sucesso',
            'usuario': usuario.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@usuarios_bp.route('/usuarios/<int:usuario_id>', methods=['DELETE'])
def deletar_usuario(usuario_id):
    """Desativar usuário (soft delete)"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        usuario_atual = get_current_user()
        if not usuario_atual:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Verificar permissões
        if usuario_atual.perfil == 'super_admin':
            # Super Admin pode desativar qualquer usuário
            pass
        elif usuario_atual.perfil == 'admin_cliente':
            # Admin do Cliente só pode desativar usuários de sua empresa
            if usuario.empresa_id != usuario_atual.empresa_id:
                return jsonify({'error': 'Acesso negado'}), 403
            # Não pode desativar Super Admin ou Admin de outras empresas
            if usuario.perfil in ['super_admin', 'admin_cliente'] and usuario.id != usuario_atual.id:
                return jsonify({'error': 'Acesso negado'}), 403
        else:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Não permitir auto-exclusão
        if usuario.id == usuario_atual.id:
            return jsonify({'error': 'Não é possível desativar seu próprio usuário'}), 400
        
        usuario.ativo = False
        usuario.data_atualizacao = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Usuário desativado com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

