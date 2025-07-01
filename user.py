from flask_sqlalchemy import SQLAlchemy

# Importar todos os modelos
from .usuario import Usuario
from .empresa import Empresa
from .denuncia import Denuncia, HistoricoDenuncia, AnexoDenuncia
from .configuracao import ConfiguracaoGlobal, ConfiguracaoEmpresa, CategoriasDenuncia, SubcategoriasDenuncia

db = SQLAlchemy()

