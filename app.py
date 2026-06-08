import streamlit as st
from database.conexao import criar_banco, SessionLocal, Demanda
from utils.tema import aplicar_tema

# 1. Configuração Global do Streamlit
st.set_page_config(page_title="Central Logística | Dias+", page_icon="🚛", layout="centered")
aplicar_tema()

# Garante que as tabelas existem
criar_banco()

# ==========================================
# ACESSO LIBERADO — APROVAÇÃO PENDENTE
# Login desativado temporariamente até aprovação da diretoria.
# Reativar: restaurar bloco de login e remover as 4 linhas abaixo.
# ==========================================
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = {
        "id": 0,
        "nome": "Acesso Demo",
        "email": "",
        "filial_base": "Praia Grande",
        "nivel_acesso": "Gestor",
    }

usuario = st.session_state.usuario_logado


# ============================================================
# BANNER DE PENDÊNCIAS — consultado a cada carregamento da home
# ============================================================
@st.cache_data(ttl=60)
def _contar_tickets_novos(filial: str, nivel_acesso: str) -> int:
    """Retorna quantos tickets estão com status 'Novo' para a filial do usuário."""
    db = SessionLocal()
    try:
        q = db.query(Demanda).filter(Demanda.status == "Novo")
        if nivel_acesso not in ("Gestor", "Admin"):
            q = q.filter(Demanda.filial_origem == filial)
        return q.count()
    finally:
        db.close()


_total_novos = _contar_tickets_novos(usuario["filial_base"], usuario["nivel_acesso"])

if _total_novos > 0:
    _label_filial = "em todas as filiais" if usuario["nivel_acesso"] in ("Gestor", "Admin") else f"em {usuario['filial_base']}"
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:0.85rem; padding:0.85rem 1.1rem;
                    background:rgba(45,197,180,0.12); border:1px solid rgba(45,197,180,0.55);
                    border-radius:10px; margin-bottom:1rem;">
            <span style="font-size:1.6rem; line-height:1;">🔔</span>
            <div style="flex:1;">
                <div style="font-family:'Barlow Condensed',sans-serif; font-weight:800;
                            text-transform:uppercase; letter-spacing:0.04em; color:#2DC5B4; font-size:1rem;">
                    {_total_novos} ticket{"s" if _total_novos > 1 else ""} aguardando triagem
                </div>
                <div style="color:rgba(255,255,255,0.65); font-size:0.85rem; margin-top:0.15rem;">
                    {_total_novos} demanda{"s" if _total_novos > 1 else ""} com status <strong style="color:#FFFFFF;">Novo</strong>
                    {_label_filial} ainda não foram assumidas. Acesse o Kanban para triar.
                </div>
            </div>
            <span style="background:#2DC5B4; color:#FFFFFF; font-weight:700; border-radius:999px;
                         padding:4px 14px; font-size:1rem; white-space:nowrap;">
                {_total_novos}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div style="padding:1.5rem 0 0.5rem;">
        <div style="font-family:'Barlow Condensed',sans-serif; font-size:2.4rem; font-weight:900;
                    text-transform:uppercase; letter-spacing:0.04em; color:#FFFFFF; line-height:1.05;">
            CENTRAL INTEGRADA DE <span style="color:#2DC5B4;">DEMANDAS</span>
        </div>
        <p style="color:rgba(255,255,255,0.5); margin-top:0.35rem; font-size:0.9rem; letter-spacing:0.04em; text-transform:uppercase;">
            Sistema Operacional &nbsp;·&nbsp; Dias+ Logística
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div style="display:flex; align-items:center; gap:0.75rem; padding:0.85rem 1.1rem;
                background:rgba(45,197,180,0.1); border:1px solid rgba(45,197,180,0.35);
                border-radius:10px; margin-bottom:1.5rem; flex-wrap:wrap;">
        <span style="font-size:1.5rem;">👤</span>
        <div>
            <span style="color:rgba(255,255,255,0.5); font-size:0.72rem; text-transform:uppercase;
                         letter-spacing:0.06em;">Acesso atual</span><br>
            <strong style="color:#FFFFFF; font-size:1.1rem;">{usuario['nome']}</strong>
            <span style="color:rgba(255,255,255,0.3); margin:0 0.5rem;">|</span>
            <span style="color:rgba(255,255,255,0.65); font-size:0.95rem;">🏢 {usuario['filial_base']}</span>
        </div>
        <div style="margin-left:auto;">
            <span style="background:#2DC5B4; color:#FFFFFF; font-weight:700; border-radius:999px;
                         padding:4px 14px; font-size:0.75rem; letter-spacing:0.05em; text-transform:uppercase;">
                {usuario['nivel_acesso']}
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="font-family:'Barlow Condensed',sans-serif; font-size:1.05rem; font-weight:800;
                text-transform:uppercase; letter-spacing:0.06em; color:rgba(255,255,255,0.5);
                margin-bottom:0.75rem;">
        Navegação do sistema
    </div>
    """,
    unsafe_allow_html=True,
)

guia_items = [
    ("📝", "1. Abertura de Ticket",  "Abra novas solicitações para a sua filial: manutenção, documentação, compras e mais."),
    ("📋", "2. Kanban Operacional",  "Visualize, mova e atualize o status das demandas em tempo real."),
    ("📊", "3. Painel Gerencial",    "KPIs, gráficos de volumetria e SLA por filial. Acesso restrito a Gestores e Admin."),
]

for icone, titulo, descricao in guia_items:
    st.markdown(
        f"""
        <div style="display:flex; align-items:flex-start; gap:0.9rem; padding:0.9rem 1.1rem;
                    background:rgba(255,255,255,0.04); border:1px solid rgba(45,197,180,0.2);
                    border-radius:10px; margin-bottom:0.6rem;">
            <span style="font-size:1.5rem; line-height:1;">{icone}</span>
            <div>
                <div style="font-family:'Barlow Condensed',sans-serif; font-size:1rem; font-weight:800;
                            text-transform:uppercase; letter-spacing:0.04em; color:#FFFFFF;">
                    {titulo}
                </div>
                <div style="color:rgba(255,255,255,0.55); font-size:0.88rem; margin-top:0.2rem;">
                    {descricao}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )