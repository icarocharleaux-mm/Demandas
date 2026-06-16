"""
Adiciona a coluna setor_destino na tabela demandas.
Rode UMA vez após o deploy: .venv\Scripts\python migrar_setor_destino.py
"""
from sqlalchemy import text
from database.conexao import engine

with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE demandas ADD COLUMN setor_destino VARCHAR(60)"))
        conn.commit()
        print("Coluna setor_destino adicionada com sucesso.")
    except Exception as e:
        if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
            print("Coluna já existe — nenhuma alteração necessária.")
        else:
            raise
