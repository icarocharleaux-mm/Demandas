from datetime import datetime
from sqlalchemy.orm import Session
from database.conexao import SessionLocal, Demanda, LogInteracao, Usuario
import bcrypt
from database.conexao import Usuario

# Dicionário auxiliar para mapear as siglas das filiais
SIGLAS_FILIAIS = {
    # SP – Capital / Grande SP
    "Carapicuíba":         "CB",
    "Guarulhos":           "GU",
    "Osasco":              "OS",
    "NASP":                "NA",
    "São Bernardo do Campo": "SB",
    "São Bernardo":        "SB",   # alias
    "São Mateus":          "SM",
    "São Matheus":         "SM",   # alias legado
    "Taboão da Serra":     "TS",
    "Barueri":             "BAR",
    "Cotia":               "CO",
    "Diadema":             "DI",
    "Embu das Artes":      "EB",
    "Ferraz de Vasconcelos": "FV",
    "Itaquaquecetuba":     "IQ",
    "Mauá":                "MU",
    "Mogi das Cruzes":     "MC",
    "Santo André":         "SA",
    "São Caetano do Sul":  "SCS",
    "Suzano":              "SZ",
    "São Paulo":           "SP",
    # SP – Litoral / Interior
    "Praia Grande":        "PG",
    "Santos":              "ST",
    "São Vicente":         "SV",
    "Cubatão":             "CUB",
    "Guarujá":             "GJ",
    "Araçatuba":           "AC",
    "Araraquara":          "AQ",   # legado
    "Bauru":               "BAU",
    "Campinas":            "CM",
    "Itapetininga":        "IP",
    "Presidente Prudente": "PP",
    "Ribeirão Preto":      "RP",
    "São José dos Campos": "SJC",
    "Sorocaba":            "SO",
    # RJ
    "Barra Mansa":         "BM",
    "Campo Grande":        "CGR",
    "Campos dos Goytacazes": "CGO",
    "Duque de Caxias":     "DC",
    "Nova Friburgo":       "NF",
    "São Gonçalo":         "SGO",
    "São Pedro da Aldeia": "SPA",
    # PR
    "Curitiba":            "CTB",
    "Ponta Grossa":        "PGR",
}

def obter_sessao():
    """Gera uma sessão do banco de dados para ser usada nas operações."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def gerar_id_ticket(db: Session, filial_nome: str) -> str:
    """
    Gera um ID único sequencial por dia e filial.
    Exemplo: LOG-PG-20260522-001
    """
    data_hoje = datetime.now()
    data_str = data_hoje.strftime("%Y%m%d")
    sigla = SIGLAS_FILIAIS.get(filial_nome, "XX")
    
    # Prefixo base para a busca: LOG-PG-20260522-%
    prefixo = f"LOG-{sigla}-{data_str}-"
    
    # Busca a última demanda desta filial no dia de hoje, ordenada de forma decrescente
    ultima_demanda = db.query(Demanda)\
        .filter(Demanda.id_ticket.like(f"{prefixo}%"))\
        .order_by(Demanda.id_ticket.desc())\
        .first()
    
    if ultima_demanda:
        # Extrai os últimos 3 dígitos (a sequência) e soma 1
        ultima_sequencia = int(ultima_demanda.id_ticket.split('-')[-1])
        nova_sequencia = ultima_sequencia + 1
    else:
        # É a primeira demanda do dia para essa filial
        nova_sequencia = 1
        
    # Formata a sequência para ter sempre 3 dígitos (ex: 001, 002)
    return f"{prefixo}{nova_sequencia:03d}"

def criar_demanda(db: Session, solicitante_id: int, filial: str, categoria: str, prioridade: str, descricao: str, prazo: datetime = None, setor_destino: str = None):
    """
    Cria uma nova demanda e registra o log inicial em uma transação atômica.
    """
    novo_id = gerar_id_ticket(db, filial)

    try:
        # 1. Cria o objeto da Demanda
        nova_demanda = Demanda(
            id_ticket=novo_id,
            solicitante_id=solicitante_id,
            filial_origem=filial,
            categoria=categoria,
            prioridade=prioridade,
            descricao=descricao,
            prazo=prazo,
            setor_destino=setor_destino,
            status="Novo"
        )
        db.add(nova_demanda)
        
        # 2. Cria o objeto do Log inicial atrelado à demanda
        log_inicial = LogInteracao(
            id_ticket=novo_id,
            usuario_id=solicitante_id,
            acao_realizada="Abertura de Ticket (Status: Novo)"
        )
        db.add(log_inicial)
        
        # 3. Consolida TUDO de uma vez
        db.commit()
        db.refresh(nova_demanda)
        return nova_demanda
        
    except Exception as e:
        # Se QUALQUER coisa der errado, cancela toda a operação e não suja o banco
        db.rollback()
        print(f"Erro ao criar demanda: {e}")
        return None

def atualizar_status_demanda(db: Session, id_ticket: str, usuario_id: int, novo_status: str, comentario_acao: str = ""):
    """
    Atualiza o status de um ticket existente e gera o rastro de auditoria.
    """
    try:
        demanda = db.query(Demanda).filter(Demanda.id_ticket == id_ticket).first()
        
        if not demanda:
            return False, "Ticket não encontrado."
            
        status_anterior = demanda.status
        
        if status_anterior == novo_status:
            return False, "O novo status é igual ao atual."

        # 1. Atualiza a demanda
        demanda.status = novo_status
        
        # 2. Registra o Log de quem alterou o quê
        acao = f"Status alterado de '{status_anterior}' para '{novo_status}'."
        if comentario_acao:
            acao += f" Motivo/Comentário: {comentario_acao}"
            
        novo_log = LogInteracao(
            id_ticket=id_ticket,
            usuario_id=usuario_id,
            acao_realizada=acao
        )
        db.add(novo_log)
        
        # 3. Executa o commit atômico
        db.commit()
        return True, "Status atualizado com sucesso."
        
    except Exception as e:
        db.rollback()
        print(f"Erro ao atualizar demanda: {e}")
        return False, "Falha na transação do banco de dados."

def listar_demandas_por_filial(db: Session, filial: str = None):
    """
    Busca as demandas. Se a filial for passada, filtra por ela (visão Operador).
    Se não for passada, traz tudo (visão Gestor/Admin).
    """
    query = db.query(Demanda)
    if filial:
        query = query.filter(Demanda.filial_origem == filial)
    return query.order_by(Demanda.data_abertura.desc()).all()

def criptografar_senha(senha: str) -> str:
    """Hash bcrypt com salt único por senha (substitui SHA-256 anterior)."""
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

def verificar_login(db: Session, email: str, senha_pura: str):
    """Busca o usuário pelo e-mail e verifica a senha com bcrypt.checkpw."""
    usuario = db.query(Usuario).filter(
        Usuario.email == email.strip().lower()
    ).first()
    if usuario and bcrypt.checkpw(senha_pura.encode(), usuario.senha_hash.encode()):
        return usuario
    return None