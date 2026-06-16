import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# 1. Carrega as variáveis do arquivo .env (que você não vai enviar pro GitHub/Railway)
load_dotenv()

# 2. Motor do Banco de Dados: Se tiver a URL do Railway, usa Postgres. Senão, cria um SQLite local.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///demandas_logistica.db")

# Ajuste necessário para o SQLAlchemy trabalhar com URLs do Postgres geradas pelo Railway
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# MODELAGEM DAS TABELAS
# ==========================================

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    nivel_acesso = Column(String(20), nullable=False) # Ex: 'Admin', 'Gestor', 'Operacao'
    filial_base = Column(String(50), nullable=False)  # Ex: 'Praia Grande', 'Osasco'
    
    # Relações
    demandas_criadas = relationship("Demanda", foreign_keys='Demanda.solicitante_id', back_populates="solicitante")
    logs = relationship("LogInteracao", back_populates="usuario")

class Demanda(Base):
    __tablename__ = "demandas"
    
    # ID customizado no formato LOG-PG-20260522-001
    id_ticket = Column(String(30), primary_key=True, index=True)
    
    # Relacionamento com o usuário que abriu
    solicitante_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    # Domínios controlados (Listas fechadas para evitar erros de digitação)
    filial_origem = Column(String(50), nullable=False) # Ex: Praia Grande, Carapicuíba
    categoria = Column(String(50), nullable=False)     # Ex: LTA / Alvará, Manutenção, Avaria
    prioridade = Column(String(20), nullable=False)    # Ex: Baixa, Média, Alta, Crítica
    status = Column(String(30), default="Novo", nullable=False)
    
    setor_destino = Column(String(60), nullable=True)
    descricao = Column(Text, nullable=False)
    prazo = Column(DateTime, nullable=True)
    data_abertura = Column(DateTime, default=datetime.now)
    
    # Relacionamentos
    solicitante = relationship("Usuario", foreign_keys=[solicitante_id], back_populates="demandas_criadas")
    logs = relationship("LogInteracao", back_populates="demanda", cascade="all, delete-orphan")

class LogInteracao(Base):
    __tablename__ = "logs_interacoes"
    
    id = Column(Integer, primary_key=True, index=True)
    id_ticket = Column(String(30), ForeignKey("demandas.id_ticket"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    acao_realizada = Column(String(255), nullable=False) # Ex: "Mudou status para Em Andamento"
    data_hora = Column(DateTime, default=datetime.now)
    
    # Relacionamentos
    demanda = relationship("Demanda", back_populates="logs")
    usuario = relationship("Usuario", back_populates="logs")

# ==========================================
# INICIALIZAÇÃO
# ==========================================
def criar_banco():
    """Cria as tabelas no banco de dados, caso não existam."""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    criar_banco()
    print("Banco de dados e tabelas criados com sucesso!")