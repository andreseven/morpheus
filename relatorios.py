from flask import Blueprint, request, jsonify, session
from src.database import db
from src.models.usuario import Usuario
from src.models.empresa import Empresa
from src.models.denuncia import Denuncia, CategoriasDenuncia
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
import json

relatorios_bp = Blueprint('relatorios', __name__)

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

@relatorios_bp.route('/relatorios/dashboard', methods=['GET'])
def relatorio_dashboard():
    """Relatório para o dashboard principal"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        usuario_atual = get_current_user()
        if not usuario_atual:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Filtrar denúncias baseado no perfil do usuário
        query_base = Denuncia.query
        
        if usuario_atual.perfil == 'super_admin':
            # Super Admin vê todas as denúncias
            pass
        elif usuario_atual.perfil in ['admin_cliente', 'auditoria', 'gerente']:
            # Usuários da empresa veem apenas denúncias da própria empresa
            query_base = query_base.filter(Denuncia.empresa_id == usuario_atual.empresa_id)
        elif usuario_atual.perfil == 'cliente':
            # Cliente vê apenas suas próprias denúncias ou anônimas
            query_base = query_base.filter(
                or_(
                    Denuncia.usuario_id == usuario_atual.id,
                    and_(Denuncia.anonima == True, Denuncia.empresa_id == usuario_atual.empresa_id)
                )
            )
        
        # Estatísticas gerais
        total_denuncias = query_base.count()
        
        # Por status
        stats_status = {}
        status_counts = query_base.with_entities(
            Denuncia.status, 
            func.count(Denuncia.id)
        ).group_by(Denuncia.status).all()
        
        for status, count in status_counts:
            stats_status[status] = count
        
        # Por prioridade
        stats_prioridade = {}
        prioridade_counts = query_base.with_entities(
            Denuncia.prioridade, 
            func.count(Denuncia.id)
        ).group_by(Denuncia.prioridade).all()
        
        for prioridade, count in prioridade_counts:
            stats_prioridade[prioridade] = count
        
        # Por categoria
        stats_categoria = {}
        categoria_counts = query_base.with_entities(
            Denuncia.categoria, 
            func.count(Denuncia.id)
        ).group_by(Denuncia.categoria).all()
        
        for categoria, count in categoria_counts:
            stats_categoria[categoria] = count
        
        # Tendência dos últimos 30 dias
        data_limite = datetime.utcnow() - timedelta(days=30)
        tendencia_query = query_base.filter(Denuncia.data_criacao >= data_limite)
        
        tendencia_diaria = {}
        for i in range(30):
            data = datetime.utcnow() - timedelta(days=i)
            data_inicio = data.replace(hour=0, minute=0, second=0, microsecond=0)
            data_fim = data_inicio + timedelta(days=1)
            
            count = tendencia_query.filter(
                and_(
                    Denuncia.data_criacao >= data_inicio,
                    Denuncia.data_criacao < data_fim
                )
            ).count()
            
            tendencia_diaria[data.strftime('%Y-%m-%d')] = count
        
        return jsonify({
            'total_denuncias': total_denuncias,
            'por_status': stats_status,
            'por_prioridade': stats_prioridade,
            'por_categoria': stats_categoria,
            'tendencia_30_dias': tendencia_diaria,
            'periodo_analise': {
                'inicio': (datetime.utcnow() - timedelta(days=30)).isoformat(),
                'fim': datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@relatorios_bp.route('/relatorios/detalhado', methods=['GET'])
def relatorio_detalhado():
    """Relatório detalhado com filtros avançados"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        usuario_atual = get_current_user()
        if not usuario_atual:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Parâmetros de filtro
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        categoria = request.args.get('categoria')
        status = request.args.get('status')
        prioridade = request.args.get('prioridade')
        empresa_id = request.args.get('empresa_id')
        
        # Query base com filtros de permissão
        query = Denuncia.query
        
        if usuario_atual.perfil == 'super_admin':
            # Super Admin pode filtrar por empresa específica
            if empresa_id:
                query = query.filter(Denuncia.empresa_id == empresa_id)
        elif usuario_atual.perfil in ['admin_cliente', 'auditoria', 'gerente']:
            # Usuários da empresa veem apenas da própria empresa
            query = query.filter(Denuncia.empresa_id == usuario_atual.empresa_id)
        elif usuario_atual.perfil == 'cliente':
            # Cliente vê apenas suas próprias denúncias ou anônimas
            query = query.filter(
                or_(
                    Denuncia.usuario_id == usuario_atual.id,
                    and_(Denuncia.anonima == True, Denuncia.empresa_id == usuario_atual.empresa_id)
                )
            )
        
        # Aplicar filtros de data
        if data_inicio:
            try:
                data_inicio_dt = datetime.fromisoformat(data_inicio.replace('Z', '+00:00'))
                query = query.filter(Denuncia.data_criacao >= data_inicio_dt)
            except ValueError:
                return jsonify({'error': 'Formato de data_inicio inválido'}), 400
        
        if data_fim:
            try:
                data_fim_dt = datetime.fromisoformat(data_fim.replace('Z', '+00:00'))
                query = query.filter(Denuncia.data_criacao <= data_fim_dt)
            except ValueError:
                return jsonify({'error': 'Formato de data_fim inválido'}), 400
        
        # Aplicar outros filtros
        if categoria:
            query = query.filter(Denuncia.categoria == categoria)
        
        if status:
            query = query.filter(Denuncia.status == status)
        
        if prioridade:
            query = query.filter(Denuncia.prioridade == prioridade)
        
        # Obter denúncias
        denuncias = query.order_by(Denuncia.data_criacao.desc()).all()
        
        # Estatísticas do período filtrado
        total = len(denuncias)
        
        # Agrupar por status
        status_stats = {}
        for denuncia in denuncias:
            status_stats[denuncia.status] = status_stats.get(denuncia.status, 0) + 1
        
        # Agrupar por categoria
        categoria_stats = {}
        for denuncia in denuncias:
            categoria_stats[denuncia.categoria] = categoria_stats.get(denuncia.categoria, 0) + 1
        
        # Agrupar por prioridade
        prioridade_stats = {}
        for denuncia in denuncias:
            prioridade_stats[denuncia.prioridade] = prioridade_stats.get(denuncia.prioridade, 0) + 1
        
        # Tempo médio de resolução (apenas para denúncias concluídas)
        denuncias_concluidas = [d for d in denuncias if d.status == 'concluida' and d.data_resolucao]
        tempo_medio_resolucao = None
        
        if denuncias_concluidas:
            total_dias = sum([
                (d.data_resolucao - d.data_criacao).days 
                for d in denuncias_concluidas
            ])
            tempo_medio_resolucao = total_dias / len(denuncias_concluidas)
        
        return jsonify({
            'filtros_aplicados': {
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'categoria': categoria,
                'status': status,
                'prioridade': prioridade,
                'empresa_id': empresa_id if usuario_atual.perfil == 'super_admin' else None
            },
            'estatisticas': {
                'total_denuncias': total,
                'por_status': status_stats,
                'por_categoria': categoria_stats,
                'por_prioridade': prioridade_stats,
                'tempo_medio_resolucao_dias': tempo_medio_resolucao
            },
            'denuncias': [d.to_dict() for d in denuncias[:100]]  # Limitar a 100 para performance
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@relatorios_bp.route('/relatorios/exportar', methods=['POST'])
def exportar_relatorio():
    """Exportar relatório em diferentes formatos"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        usuario_atual = get_current_user()
        if not usuario_atual:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        formato = data.get('formato', 'json')  # json, csv, pdf
        filtros = data.get('filtros', {})
        
        # Aplicar mesma lógica de filtros do relatório detalhado
        query = Denuncia.query
        
        if usuario_atual.perfil == 'super_admin':
            if filtros.get('empresa_id'):
                query = query.filter(Denuncia.empresa_id == filtros['empresa_id'])
        elif usuario_atual.perfil in ['admin_cliente', 'auditoria', 'gerente']:
            query = query.filter(Denuncia.empresa_id == usuario_atual.empresa_id)
        elif usuario_atual.perfil == 'cliente':
            query = query.filter(
                or_(
                    Denuncia.usuario_id == usuario_atual.id,
                    and_(Denuncia.anonima == True, Denuncia.empresa_id == usuario_atual.empresa_id)
                )
            )
        
        # Aplicar filtros de data
        if filtros.get('data_inicio'):
            data_inicio_dt = datetime.fromisoformat(filtros['data_inicio'].replace('Z', '+00:00'))
            query = query.filter(Denuncia.data_criacao >= data_inicio_dt)
        
        if filtros.get('data_fim'):
            data_fim_dt = datetime.fromisoformat(filtros['data_fim'].replace('Z', '+00:00'))
            query = query.filter(Denuncia.data_criacao <= data_fim_dt)
        
        if filtros.get('categoria'):
            query = query.filter(Denuncia.categoria == filtros['categoria'])
        
        if filtros.get('status'):
            query = query.filter(Denuncia.status == filtros['status'])
        
        if filtros.get('prioridade'):
            query = query.filter(Denuncia.prioridade == filtros['prioridade'])
        
        denuncias = query.order_by(Denuncia.data_criacao.desc()).all()
        
        if formato == 'json':
            return jsonify({
                'denuncias': [d.to_dict() for d in denuncias],
                'total': len(denuncias),
                'data_exportacao': datetime.utcnow().isoformat()
            }), 200
        
        elif formato == 'csv':
            # Para CSV, retornar dados estruturados que o frontend pode processar
            csv_data = []
            for d in denuncias:
                csv_data.append({
                    'Protocolo': d.protocolo,
                    'Título': d.titulo,
                    'Categoria': d.categoria,
                    'Subcategoria': d.subcategoria,
                    'Status': d.status,
                    'Prioridade': d.prioridade,
                    'Data Criação': d.data_criacao.strftime('%d/%m/%Y %H:%M') if d.data_criacao else '',
                    'Anônima': 'Sim' if d.anonima else 'Não',
                    'Origem': d.origem
                })
            
            return jsonify({
                'formato': 'csv',
                'dados': csv_data,
                'total': len(csv_data),
                'data_exportacao': datetime.utcnow().isoformat()
            }), 200
        
        else:
            return jsonify({'error': 'Formato não suportado'}), 400
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@relatorios_bp.route('/relatorios/metricas-empresa', methods=['GET'])
def metricas_empresa():
    """Métricas específicas por empresa (apenas Super Admin)"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        usuario_atual = get_current_user()
        if not usuario_atual or usuario_atual.perfil != 'super_admin':
            return jsonify({'error': 'Acesso negado - apenas Super Admin'}), 403
        
        # Obter todas as empresas
        empresas = Empresa.query.filter_by(status='ativa').all()
        
        metricas = []
        for empresa in empresas:
            # Estatísticas da empresa
            total_denuncias = Denuncia.query.filter_by(empresa_id=empresa.id).count()
            total_usuarios = Usuario.query.filter_by(empresa_id=empresa.id, ativo=True).count()
            
            # Denúncias por status
            status_counts = db.session.query(
                Denuncia.status, 
                func.count(Denuncia.id)
            ).filter_by(empresa_id=empresa.id).group_by(Denuncia.status).all()
            
            status_stats = {status: count for status, count in status_counts}
            
            # Denúncias dos últimos 30 dias
            data_limite = datetime.utcnow() - timedelta(days=30)
            denuncias_recentes = Denuncia.query.filter(
                and_(
                    Denuncia.empresa_id == empresa.id,
                    Denuncia.data_criacao >= data_limite
                )
            ).count()
            
            metricas.append({
                'empresa': empresa.to_dict(),
                'estatisticas': {
                    'total_denuncias': total_denuncias,
                    'total_usuarios': total_usuarios,
                    'denuncias_30_dias': denuncias_recentes,
                    'por_status': status_stats
                }
            })
        
        return jsonify({
            'metricas_empresas': metricas,
            'total_empresas': len(empresas),
            'data_consulta': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

