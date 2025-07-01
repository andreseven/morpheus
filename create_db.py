import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.database import db

def create_database():
    """Criar todas as tabelas do banco de dados"""
    with app.app_context():
        db.create_all()
        print("Banco de dados criado com sucesso!")

if __name__ == "__main__":
    create_database()

