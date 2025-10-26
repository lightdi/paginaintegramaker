#!/usr/bin/env python3
"""
Modelos do banco de dados para Integra Maker
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

# Instância do banco de dados será importada do app.py
db = SQLAlchemy()

class Usuario(db.Model):
    """Modelo para usuários do sistema"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    email_confirmado = db.Column(db.Boolean, default=False)
    token_confirmacao = db.Column(db.String(100), unique=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_confirmacao = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Define a senha do usuário com hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    def gerar_token_confirmacao(self):
        """Gera token único para confirmação de email"""
        self.token_confirmacao = secrets.token_urlsafe(32)
        return self.token_confirmacao
    
    def confirmar_email(self):
        """Confirma o email do usuário"""
        self.email_confirmado = True
        self.data_confirmacao = datetime.utcnow()
        self.token_confirmacao = None
    
    def __repr__(self):
        return f'<Usuario {self.username}>'

class Projeto(db.Model):
    """Modelo para projetos do Integra Maker"""
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    equipe = db.Column(db.String(200), nullable=False)
    disciplina = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='ativo')  # ativo, concluido
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_conclusao = db.Column(db.DateTime)
    imagem_url = db.Column(db.String(200))
    tecnologias = db.Column(db.String(200))
    
    def __repr__(self):
        return f'<Projeto {self.titulo}>'

class Noticia(db.Model):
    """Modelo para notícias do Integra Maker"""
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    data_publicacao = db.Column(db.DateTime, default=datetime.utcnow)
    imagem_url = db.Column(db.String(200))
    
    def __repr__(self):
        return f'<Noticia {self.titulo}>'
