#!/usr/bin/env python3
"""
Script para criar usuário administrador padrão
Execute este script para criar o primeiro usuário admin do sistema
"""

from app import app
from models import db, Usuario

def criar_admin_padrao():
    """Cria um usuário administrador padrão"""
    
    with app.app_context():
        # Verificar se já existe um admin
        admin_existente = Usuario.query.filter_by(is_admin=True).first()
        if admin_existente:
            print("Ja existe um usuario administrador no sistema!")
            print(f"   Username: {admin_existente.username}")
            print(f"   Email: {admin_existente.email}")
            return
        
        # Criar usuário administrador padrão
        admin = Usuario(
            username='admin',
            email='admin@ifpb.edu.br',
            nome='Administrador Integra Maker',
            is_admin=True,
            email_confirmado=True  # Admin já confirmado
        )
        admin.set_password('admin123')  # Senha padrão
        
        db.session.add(admin)
        db.session.commit()
        
        print("Usuario administrador criado com sucesso!")
        print("Credenciais de acesso:")
        print(f"   Username: admin")
        print(f"   Senha: admin123")
        print(f"   Email: admin@ifpb.edu.br")
        print("\nIMPORTANTE: Altere a senha padrao apos o primeiro login!")
        print("Acesse: http://localhost:5000/login")

if __name__ == "__main__":
    criar_admin_padrao()
