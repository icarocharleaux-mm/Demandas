from database.conexao import SessionLocal, Usuario
from database.operacoes_crud import criptografar_senha

def cadastrar_usuarios_teste():
    db = SessionLocal()
    try:
        # Lista de funcionários de teste para cada filial
        usuarios_para_criar = [
            {"nome": "Icaro Gestor", "email": "icaro@empresa.com", "senha": "123", "acesso": "Gestor", "filial": "Praia Grande"},
            {"nome": "Marcos Osasco", "email": "marcos@empresa.com", "senha": "123", "acesso": "Operacao", "filial": "Osasco"},
            {"nome": "Ana Carapicuiba", "email": "ana@empresa.com", "senha": "123", "acesso": "Operacao", "filial": "Carapicuíba"},
            {"nome": "Silvia S Bernardo", "email": "silvia@empresa.com", "senha": "123", "acesso": "Operacao", "filial": "São Bernardo"}
        ]
        
        for u in usuarios_para_criar:
            # Verifica se já não existe
            existe = db.query(Usuario).filter(Usuario.email == u["email"]).first()
            if not existe:
                novo_usuario = Usuario(
                    nome=u["nome"],
                    email=u["email"],
                    senha_hash=criptografar_senha(u["senha"]),
                    nivel_acesso=u["acesso"],
                    filial_base=u["filial"]
                )
                db.add(novo_usuario)
        
        db.commit()
        print("Funcionários de teste cadastrados com sucesso!")
    except Exception as e:
        db.rollback()
        print(f"Erro ao cadastrar: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    cadastrar_usuarios_teste()