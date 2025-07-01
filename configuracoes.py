from flask import Blueprint, request, jsonify, session
from src.database import db
from src.models.usuario import Usuario
from src.models.empresa import Empresa
from src.models.denuncia import CategoriasDenuncia, SubcategoriasDenuncia
from datetime import datetime
import json

configuracoes_bp = Blueprint('configuracoes', __name__)

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

def require_admin():
    """Verificar se o usuário é admin"""
    usuario = get_current_user()
    if not usuario or usuario.perfil not in ['super_admin', 'admin_cliente']:
        return jsonify({'error': 'Acesso negado - apenas administradores'}), 403
    return None

@configuracoes_bp.route('/configuracoes/empresa', methods=['GET'])
def obter_configuracoes_empresa():
    """Obter configurações da empresa do usuário logado"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        usuario_atual = get_current_user()
        if not usuario_atual:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        if usuario_atual.perfil == 'super_admin':
            # Super Admin pode ver configurações de qualquer empresa
            empresa_id = request.args.get('empresa_id')
            if not empresa_id:
                return jsonify({'error': 'empresa_id é obrigatório para Super Admin'}), 400
            empresa = Empresa.query.get(empresa_id)
        else:
            # Outros usuários veem apenas da própria empresa
            empresa = Empresa.query.get(usuario_atual.empresa_id)
        
        if not empresa:
            return jsonify({'error': 'Empresa não encontrada'}), 404
        
        return jsonify({
            'empresa': empresa.to_dict(),
            'configuracoes': {
                'logo_url': empresa.logo_url,
                'cores_personalizadas': json.loads(empresa.cores_personalizadas) if empresa.cores_personalizadas else {},
                'nome': empresa.nome,
                'cnpj': empresa.cnpj,
                'status': empresa.status
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@configuracoes_bp.route('/configuracoes/empresa', methods=['PUT'])
def atualizar_configuracoes_empresa():
    """Atualizar configurações da empresa"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    admin_error = require_admin()
    if admin_error:
        return admin_error
    
    try:
        usuario_atual = get_current_user()
        data = request.get_json()
        
        if usuario_atual.perfil == 'super_admin':
            # Super Admin pode atualizar qualquer empresa
            empresa_id = data.get('empresa_id')
            if not empresa_id:
                return jsonify({'error': 'empresa_id é obrigatório para Super Admin'}), 400
            empresa = Empresa.query.get(empresa_id)
        else:
            # Admin Cliente atualiza apenas a própria empresa
            empresa = Empresa.query.get(usuario_atual.empresa_id)
        
        if not empresa:
            return jsonify({'error': 'Empresa não encontrada'}), 404
        
        # Atualizar campos permitidos
        if 'nome' in data:
            empresa.nome = data['nome']
        
        if 'logo_url' in data:
            empresa.logo_url = data['logo_url']
        
        if 'cores_personalizadas' in data:
            empresa.cores_personalizadas = json.dumps(data['cores_personalizadas'])
        
        # Apenas Super Admin pode alterar status
        if 'status' in data and usuario_atual.perfil == 'super_admin':
            empresa.status = data['status']
        
        empresa.data_atualizacao = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Configurações atualizadas com sucesso',
            'empresa': empresa.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@configuracoes_bp.route('/configuracoes/categorias', methods=['GET'])
def obter_configuracoes_categorias():
    """Obter configurações de categorias"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        categorias = CategoriasDenuncia.query.order_by(CategoriasDenuncia.ordem).all()
        
        resultado = []
        for categoria in categorias:
            subcategorias = SubcategoriasDenuncia.query.filter_by(
                categoria_id=categoria.id
            ).order_by(SubcategoriasDenuncia.ordem).all()
            
            categoria_dict = categoria.to_dict()
            categoria_dict['subcategorias'] = [sub.to_dict() for sub in subcategorias]
            resultado.append(categoria_dict)
        
        return jsonify({'categorias': resultado}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@configuracoes_bp.route('/configuracoes/categorias', methods=['POST'])
def criar_categoria():
    """Criar nova categoria"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    admin_error = require_admin()
    if admin_error:
        return admin_error
    
    try:
        data = request.get_json()
        
        if not data.get('nome'):
            return jsonify({'error': 'Nome da categoria é obrigatório'}), 400
        
        # Verificar se já existe categoria com mesmo nome
        categoria_existente = CategoriasDenuncia.query.filter_by(nome=data['nome']).first()
        if categoria_existente:
            return jsonify({'error': 'Já existe uma categoria com este nome'}), 400
        
        # Obter próxima ordem
        max_ordem = db.session.query(db.func.max(CategoriasDenuncia.ordem)).scalar() or 0
        
        nova_categoria = CategoriasDenuncia(
            nome=data['nome'],
            descricao=data.get('descricao', ''),
            ativa=data.get('ativa', True),
            ordem=max_ordem + 1
        )
        
        db.session.add(nova_categoria)
        db.session.commit()
        
        return jsonify({
            'message': 'Categoria criada com sucesso',
            'categoria': nova_categoria.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@configuracoes_bp.route('/configuracoes/categorias/<int:categoria_id>', methods=['PUT'])
def atualizar_categoria(categoria_id):
    """Atualizar categoria existente"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    admin_error = require_admin()
    if admin_error:
        return admin_error
    
    try:
        categoria = CategoriasDenuncia.query.get(categoria_id)
        if not categoria:
            return jsonify({'error': 'Categoria não encontrada'}), 404
        
        data = request.get_json()
        
        if 'nome' in data:
            # Verificar se já existe outra categoria com mesmo nome
            categoria_existente = CategoriasDenuncia.query.filter(
                CategoriasDenuncia.nome == data['nome'],
                CategoriasDenuncia.id != categoria_id
            ).first()
            if categoria_existente:
                return jsonify({'error': 'Já existe uma categoria com este nome'}), 400
            categoria.nome = data['nome']
        
        if 'descricao' in data:
            categoria.descricao = data['descricao']
        
        if 'ativa' in data:
            categoria.ativa = data['ativa']
        
        if 'ordem' in data:
            categoria.ordem = data['ordem']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Categoria atualizada com sucesso',
            'categoria': categoria.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@configuracoes_bp.route('/configuracoes/subcategorias', methods=['POST'])
def criar_subcategoria():
    """Criar nova subcategoria"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    admin_error = require_admin()
    if admin_error:
        return admin_error
    
    try:
        data = request.get_json()
        
        if not data.get('nome') or not data.get('categoria_id'):
            return jsonify({'error': 'Nome e categoria_id são obrigatórios'}), 400
        
        # Verificar se categoria existe
        categoria = CategoriasDenuncia.query.get(data['categoria_id'])
        if not categoria:
            return jsonify({'error': 'Categoria não encontrada'}), 404
        
        # Verificar se já existe subcategoria com mesmo nome na categoria
        subcategoria_existente = SubcategoriasDenuncia.query.filter_by(
            categoria_id=data['categoria_id'],
            nome=data['nome']
        ).first()
        if subcategoria_existente:
            return jsonify({'error': 'Já existe uma subcategoria com este nome nesta categoria'}), 400
        
        # Obter próxima ordem
        max_ordem = db.session.query(db.func.max(SubcategoriasDenuncia.ordem)).filter_by(
            categoria_id=data['categoria_id']
        ).scalar() or 0
        
        nova_subcategoria = SubcategoriasDenuncia(
            categoria_id=data['categoria_id'],
            nome=data['nome'],
            descricao=data.get('descricao', ''),
            ativa=data.get('ativa', True),
            ordem=max_ordem + 1
        )
        
        db.session.add(nova_subcategoria)
        db.session.commit()
        
        return jsonify({
            'message': 'Subcategoria criada com sucesso',
            'subcategoria': nova_subcategoria.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@configuracoes_bp.route('/configuracoes/subcategorias/<int:subcategoria_id>', methods=['PUT'])
def atualizar_subcategoria(subcategoria_id):
    """Atualizar subcategoria existente"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    admin_error = require_admin()
    if admin_error:
        return admin_error
    
    try:
        subcategoria = SubcategoriasDenuncia.query.get(subcategoria_id)
        if not subcategoria:
            return jsonify({'error': 'Subcategoria não encontrada'}), 404
        
        data = request.get_json()
        
        if 'nome' in data:
            # Verificar se já existe outra subcategoria com mesmo nome na categoria
            subcategoria_existente = SubcategoriasDenuncia.query.filter(
                SubcategoriasDenuncia.nome == data['nome'],
                SubcategoriasDenuncia.categoria_id == subcategoria.categoria_id,
                SubcategoriasDenuncia.id != subcategoria_id
            ).first()
            if subcategoria_existente:
                return jsonify({'error': 'Já existe uma subcategoria com este nome nesta categoria'}), 400
            subcategoria.nome = data['nome']
        
        if 'descricao' in data:
            subcategoria.descricao = data['descricao']
        
        if 'ativa' in data:
            subcategoria.ativa = data['ativa']
        
        if 'ordem' in data:
            subcategoria.ordem = data['ordem']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Subcategoria atualizada com sucesso',
            'subcategoria': subcategoria.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@configuracoes_bp.route('/configuracoes/sistema', methods=['GET'])
def obter_configuracoes_sistema():
    """Obter configurações gerais do sistema (apenas Super Admin)"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        usuario_atual = get_current_user()
        if usuario_atual.perfil != 'super_admin':
            return jsonify({'error': 'Acesso negado - apenas Super Admin'}), 403
        
        # Estatísticas gerais do sistema
        total_empresas = Empresa.query.count()
        empresas_ativas = Empresa.query.filter_by(status='ativa').count()
        total_usuarios = Usuario.query.count()
        usuarios_ativos = Usuario.query.filter_by(ativo=True).count()
        
        return jsonify({
            'estatisticas': {
                'total_empresas': total_empresas,
                'empresas_ativas': empresas_ativas,
                'total_usuarios': total_usuarios,
                'usuarios_ativos': usuarios_ativos
            },
            'configuracoes': {
                'versao_sistema': '1.0.0',
                'ambiente': 'desenvolvimento'
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

