from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash
from datetime import datetime
from src.database import db
from src.models.usuario import Usuario

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint para login de usuários"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('senha'):
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        email = data['email'].lower().strip()
        senha = data['senha']
        
        # Buscar usuário por email
        usuario = Usuario.query.filter_by(email=email).first()
        
        if not usuario:
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        if not usuario.ativo:
            return jsonify({'error': 'Usuário inativo'}), 401
        
        if not usuario.check_senha(senha):
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        # Atualizar último login
        usuario.ultimo_login = datetime.utcnow()
        db.session.commit()
        
        # Criar sessão
        session['user_id'] = usuario.id
        session['user_perfil'] = usuario.perfil
        session['empresa_id'] = usuario.empresa_id
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'usuario': usuario.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Endpoint para logout de usuários"""
    try:
        session.clear()
        return jsonify({'message': 'Logout realizado com sucesso'}), 200
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Endpoint para obter informações do usuário logado"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        usuario = Usuario.query.get(session['user_id'])
        
        if not usuario or not usuario.ativo:
            session.clear()
            return jsonify({'error': 'Usuário não encontrado ou inativo'}), 401
        
        return jsonify({
            'usuario': usuario.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/check-session', methods=['GET'])
def check_session():
    """Endpoint para verificar se há uma sessão ativa"""
    try:
        if 'user_id' in session:
            return jsonify({'authenticated': True}), 200
        else:
            return jsonify({'authenticated': False}), 200
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

