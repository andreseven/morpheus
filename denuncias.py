from flask import Blueprint, request, jsonify, session
from src.database import db
from src.models.usuario import Usuario
from src.models.empresa import Empresa
from src.models.denuncia import Denuncia, HistoricoDenuncia, CategoriasDenuncia, SubcategoriasDenuncia
from datetime import datetime
import os

denuncias_bp = Blueprint('denuncias', __name__)

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

@denuncias_bp.route('/denuncias', methods=['GET'])
def listar_denuncias():
    """Listar denúncias baseado no perfil do usuário logado"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        usuario_atual = get_current_user()
        if not usuario_atual:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Filtros de query
        status = request.args.get('status')
        categoria = request.args.get('categoria')
        prioridade = request.args.get('prioridade')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Construir query baseada no perfil
        query = Denuncia.query
        
        if usuario_atual.perfil == 'super_admin':
            # Super Admin pode ver todas as denúncias
            pass
        elif usuario_atual.perfil in ['admin_cliente', 'auditoria']:
            # Admin do Cliente e Auditoria veem denúncias de sua empresa
            query = query.filter_by(empresa_id=usuario_atual.empresa_id)
        elif usuario_atual.perfil == 'gerente':
            # Gerente vê denúncias de sua empresa
            query = query.filter_by(empresa_id=usuario_atual.empresa_id)
        elif usuario_atual.perfil == 'cliente':
            # Cliente vê apenas suas próprias denúncias
            query = query.filter_by(usuario_id=usuario_atual.id)
        else:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Aplicar filtros
        if status:
            query = query.filter_by(status=status)
        if categoria:
            query = query.filter_by(categoria=categoria)
        if prioridade:
            query = query.filter_by(prioridade=prioridade)
        
        # Ordenar por data de criação (mais recentes primeiro)
        query = query.order_by(Denuncia.data_criacao.desc())
        
        # Paginação
        denuncias_paginadas = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'denuncias': [denuncia.to_dict() for denuncia in denuncias_paginadas.items],
            'total': denuncias_paginadas.total,
            'pages': denuncias_paginadas.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@denuncias_bp.route('/denuncias', methods=['POST'])
def criar_denuncia():
    """Criar nova denúncia"""
    try:
        data = request.get_json()
        
        # Validações básicas
        required_fields = ['titulo', 'descricao', 'categoria']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Verificar se é denúncia anônima ou de usuário logado
        usuario_atual = get_current_user()
        anonima = data.get('anonima', False)
        
        if not anonima and not usuario_atual:
            return jsonify({'error': 'Usuário deve estar logado para denúncia não anônima'}), 401
        
        # Determinar empresa
        empresa_id = None
        if usuario_atual:
            empresa_id = usuario_atual.empresa_id
        else:
            # Para denúncias anônimas, pode ser especificada a empresa
            empresa_id = data.get('empresa_id')
            if not empresa_id:
                return jsonify({'error': 'Empresa deve ser especificada para denúncia anônima'}), 400
        
        # Verificar se empresa existe
        empresa = Empresa.query.get(empresa_id)
        if not empresa:
            return jsonify({'error': 'Empresa não encontrada'}), 404
        
        # Gerar protocolo único
        protocolo = Denuncia.gerar_protocolo()
        while Denuncia.query.filter_by(protocolo=protocolo).first():
            protocolo = Denuncia.gerar_protocolo()
        
        # Criar nova denúncia
        nova_denuncia = Denuncia(
            protocolo=protocolo,
            titulo=data['titulo'],
            descricao=data['descricao'],
            categoria=data['categoria'],
            subcategoria=data.get('subcategoria'),
            prioridade=data.get('prioridade', 'media'),
            anonima=anonima,
            usuario_id=usuario_atual.id if usuario_atual and not anonima else None,
            empresa_id=empresa_id,
            origem=data.get('origem', 'web'),
            ip_origem=request.remote_addr
        )
        
        db.session.add(nova_denuncia)
        db.session.flush()  # Para obter o ID
        
        # Criar histórico
        historico = HistoricoDenuncia(
            denuncia_id=nova_denuncia.id,
            usuario_id=usuario_atual.id if usuario_atual else None,
            acao='criada',
            descricao='Denúncia criada',
            status_novo='recebida'
        )
        db.session.add(historico)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Denúncia criada com sucesso',
            'denuncia': nova_denuncia.to_dict(),
            'protocolo': protocolo
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@denuncias_bp.route('/denuncias/<int:denuncia_id>', methods=['GET'])
def obter_denuncia(denuncia_id):
    """Obter detalhes de uma denúncia específica"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        usuario_atual = get_current_user()
        if not usuario_atual:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        denuncia = Denuncia.query.get(denuncia_id)
        if not denuncia:
            return jsonify({'error': 'Denúncia não encontrada'}), 404
        
        # Verificar permissões
        if not usuario_atual.can_view_denuncia(denuncia):
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Obter histórico
        historico = HistoricoDenuncia.query.filter_by(denuncia_id=denuncia_id).order_by(HistoricoDenuncia.data_acao.desc()).all()
        
        return jsonify({
            'denuncia': denuncia.to_dict(include_sensitive=True),
            'historico': [h.to_dict() for h in historico]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@denuncias_bp.route('/denuncias/<int:denuncia_id>/status', methods=['PUT'])
def atualizar_status_denuncia(denuncia_id):
    """Atualizar status de uma denúncia"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        usuario_atual = get_current_user()
        if not usuario_atual:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Apenas Admin Cliente, Auditoria e Super Admin podem alterar status
        if usuario_atual.perfil not in ['super_admin', 'admin_cliente', 'auditoria']:
            return jsonify({'error': 'Acesso negado'}), 403
        
        denuncia = Denuncia.query.get(denuncia_id)
        if not denuncia:
            return jsonify({'error': 'Denúncia não encontrada'}), 404
        
        # Verificar se pode gerenciar esta denúncia
        if usuario_atual.perfil != 'super_admin' and denuncia.empresa_id != usuario_atual.empresa_id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        novo_status = data.get('status')
        comentario = data.get('comentario', '')
        
        if not novo_status:
            return jsonify({'error': 'Status é obrigatório'}), 400
        
        status_validos = ['recebida', 'em_analise', 'concluida', 'arquivada']
        if novo_status not in status_validos:
            return jsonify({'error': 'Status inválido'}), 400
        
        status_anterior = denuncia.status
        denuncia.status = novo_status
        denuncia.responsavel_id = usuario_atual.id
        
        if novo_status == 'concluida':
            denuncia.data_conclusao = datetime.utcnow()
        
        # Criar histórico
        historico = HistoricoDenuncia(
            denuncia_id=denuncia.id,
            usuario_id=usuario_atual.id,
            acao='status_alterado',
            descricao=f'Status alterado de "{status_anterior}" para "{novo_status}". {comentario}',
            status_anterior=status_anterior,
            status_novo=novo_status
        )
        db.session.add(historico)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Status atualizado com sucesso',
            'denuncia': denuncia.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@denuncias_bp.route('/categorias', methods=['GET'])
def listar_categorias():
    """Listar categorias de denúncias"""
    try:
        categorias = CategoriasDenuncia.query.filter_by(ativa=True).order_by(CategoriasDenuncia.ordem).all()
        
        resultado = []
        for categoria in categorias:
            subcategorias = SubcategoriasDenuncia.query.filter_by(
                categoria_id=categoria.id, 
                ativa=True
            ).order_by(SubcategoriasDenuncia.ordem).all()
            
            categoria_dict = categoria.to_dict()
            categoria_dict['subcategorias'] = [sub.to_dict() for sub in subcategorias]
            resultado.append(categoria_dict)
        
        return jsonify({'categorias': resultado}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@denuncias_bp.route('/denuncias/estatisticas', methods=['GET'])
def obter_estatisticas():
    """Obter estatísticas de denúncias"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        usuario_atual = get_current_user()
        if not usuario_atual:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Construir query baseada no perfil
        query = Denuncia.query
        
        if usuario_atual.perfil == 'super_admin':
            # Super Admin pode ver todas as denúncias
            pass
        elif usuario_atual.perfil in ['admin_cliente', 'auditoria', 'gerente']:
            # Admin do Cliente, Auditoria e Gerente veem denúncias de sua empresa
            query = query.filter_by(empresa_id=usuario_atual.empresa_id)
        elif usuario_atual.perfil == 'cliente':
            # Cliente vê apenas suas próprias denúncias
            query = query.filter_by(usuario_id=usuario_atual.id)
        else:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Calcular estatísticas
        total = query.count()
        recebidas = query.filter_by(status='recebida').count()
        em_analise = query.filter_by(status='em_analise').count()
        concluidas = query.filter_by(status='concluida').count()
        arquivadas = query.filter_by(status='arquivada').count()
        
        # Estatísticas por categoria
        categorias_stats = db.session.query(
            Denuncia.categoria,
            db.func.count(Denuncia.id).label('total')
        ).filter(
            query.whereclause if query.whereclause is not None else True
        ).group_by(Denuncia.categoria).all()
        
        return jsonify({
            'total': total,
            'por_status': {
                'recebidas': recebidas,
                'em_analise': em_analise,
                'concluidas': concluidas,
                'arquivadas': arquivadas
            },
            'por_categoria': [
                {'categoria': cat, 'total': total} 
                for cat, total in categorias_stats
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

