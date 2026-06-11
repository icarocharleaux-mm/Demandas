from database.conexao import SessionLocal, Usuario
from database.operacoes_crud import criptografar_senha


USUARIOS = [
    # ── Gestor principal ────────────────────────────────────────────────────
    {
        "nome":    "Icaro Nascimento",
        "email":   "icaro.nascimento@mmdeliverytransportes.com.br",
        "senha":   "123456",
        "acesso":  "Gestor",
        "filial":  "Praia Grande",
    },

    # ── Gerentes regionais ──────────────────────────────────────────────────
    {
        "nome":   "Rodrigo Dupim",
        "email":  "rodrigo.dupim@diaslog.com.br",
        "senha":  "123",
        "acesso": "Operacao",
        "filial": "Praia Grande",
    },
    {
        "nome":   "Edson Silva",
        "email":  "edson.silva@mmdeliverytransportes.com.br",
        "senha":  "123",
        "acesso": "Operacao",
        "filial": "Carapicuíba",
    },
    {
        "nome":   "Wilton Silva",
        "email":  "wilton.silva@mmdeliverytransportes.com.br",
        "senha":  "123",
        "acesso": "Operacao",
        "filial": "Araçatuba",
    },
    {
        "nome":   "Helder Rodrigues",
        "email":  "helder.rodrigues@mddelivery.com.br",
        "senha":  "123",
        "acesso": "Operacao",
        "filial": "Barra Mansa",
    },

    # ── SP Interior ─────────────────────────────────────────────────────────
    {
        "nome":   "Yago Fernando",
        "email":  "yago.fernando@mmdeliverytransportes.com.br",
        "senha":  "123",
        "acesso": "Operacao",
        "filial": "Araçatuba",
    },
    {
        "nome":   "Antenor Hugo",
        "email":  "antenor.hugo@mddelivery.com.br",
        "senha":  "123",
        "acesso": "Operacao",
        "filial": "Ribeirão Preto",
    },
    {
        "nome":   "Leandro Policarpo",
        "email":  "leandro.silva@mddelivery.com.br",
        "senha":  "123",
        "acesso": "Operacao",
        "filial": "Campinas",
    },
    {
        "nome":   "Robison Lima",
        "email":  "robison.lima@mddelivery.com.br",
        "senha":  "123",
        "acesso": "Operacao",
        "filial": "Campinas",
    },
    {
        "nome":   "Alex Peres",
        "email":  "alex.peres@mmdeliverytransportes.com.br",
        "senha":  "123",
        "acesso": "Operacao",
        "filial": "Praia Grande",
    },
    {
        "nome":   "Rodrigo Carlos",
        "email":  "rodrigo.rodrigues@mmdeliverytransportes.com.br",
        "senha":  "123",
        "acesso": "Operacao",
        "filial": "São José dos Campos",
    },
    {
        "nome":   "Andressa Ramires",
        "email":  "andressa.ramires@mmdeliverytransportes.com.br",
        "senha":  "123",
        "acesso": "Operacao",
        "filial": "São José dos Campos",
    },

    # ── SP Capital ──────────────────────────────────────────────────────────
    {
        "nome":   "Alexandre Chagas",
        "email":  "alexandre.chagas@mmdeliverytransportes.com.br",
        "senha":  "123",
        "acesso": "Operacao",
        "filial": "Carapicuíba",
    },
    {
        "nome":   "Flávio Santos",
        "email":  "flavio.santos@mmdeliverytransportes.com.br",
        "senha":  "123",
        "acesso": "Operacao",
        "filial": "Carapicuíba",
    },
    {
        "nome":   "Gilvan Oliveira",
        "email":  "gilvan.oliveira@mmdeliverytransportes.com.br",
        "senha":  "123",
        "acesso": "Operacao",
        "filial": "Osasco",
    },
    {
        "nome":   "Rildo Araújo",
        "email":  "rildo.araujo@mmdeliverytransportes.com.br",
        "senha":  "123",
        "acesso": "Operacao",
        "filial": "Osasco",
    },
    {
        "nome":   "Lucas Oliveira",
        "email":  "lucas.oliveira@mmdeliverytransportes.com.br",
        "senha":  "123",
        "acesso": "Operacao",
        "filial": "NASP",
    },
    {
        "nome":   "Marcio Rollo",
        "email":  "marcio.rollo@diaslog.com.br",
        "senha":  "123",
        "acesso": "Operacao",
        "filial": "Guarulhos",
    },

    # ── RJ ──────────────────────────────────────────────────────────────────
    {
        "nome":   "Leonardo Oliveira",
        "email":  "leonardo.oliveira@mddelivery.com.br",
        "senha":  "123",
        "acesso": "Operacao",
        "filial": "Barra Mansa",
    },
    {
        "nome":   "Sara Souza",
        "email":  "sara.souza@mddelivery.com.br",
        "senha":  "123",
        "acesso": "Operacao",
        "filial": "Campos dos Goytacazes",
    },
    {
        "nome":   "Laerte Martins",
        "email":  "laerte.martins@mddelivery.com.br",
        "senha":  "123",
        "acesso": "Operacao",
        "filial": "Duque de Caxias",
    },
    {
        "nome":   "Arthur Rodrigues",
        "email":  "arthur.rodrigues@mddelivery.com.br",
        "senha":  "123",
        "acesso": "Operacao",
        "filial": "São Gonçalo",
    },

    # ── PR ──────────────────────────────────────────────────────────────────
    {
        "nome":   "Jefferson Marques",
        "email":  "jefferson.marques@fastty.com.br",
        "senha":  "123",
        "acesso": "Operacao",
        "filial": "Curitiba",
    },
    {
        "nome":   "Sandy Mara",
        "email":  "sandy.mara@fastty.com.br",
        "senha":  "123",
        "acesso": "Operacao",
        "filial": "Curitiba",
    },
]


def seed():
    db = SessionLocal()
    criados, ignorados = 0, 0
    try:
        for u in USUARIOS:
            email = u["email"].strip().lower()
            if db.query(Usuario).filter(Usuario.email == email).first():
                ignorados += 1
                continue
            db.add(Usuario(
                nome=u["nome"],
                email=email,
                senha_hash=criptografar_senha(u["senha"]),
                nivel_acesso=u["acesso"],
                filial_base=u["filial"],
            ))
            criados += 1
        db.commit()
        print(f"Concluído: {criados} criado(s), {ignorados} já existia(m).")
    except Exception as e:
        db.rollback()
        print(f"Erro: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
