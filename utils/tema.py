import streamlit as st
import os

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@300;400;600;700;800;900&display=swap');

/* ===== FUNDO GERAL ===== */
[data-testid="stAppViewContainer"],
.stApp {
    background: linear-gradient(135deg, #0B2E3A 0%, #1D7A8A 100%) !important;
}
[data-testid="stHeader"] {
    background: rgba(11,46,58,0.88) !important;
    backdrop-filter: blur(8px) !important;
    border-bottom: 1px solid rgba(45,197,180,0.25) !important;
}
.main .block-container {
    background: transparent !important;
}
/* ===== FONTE BARLOW CONDENSED — seletores cirúrgicos, SEM body/*, SEM herança ===== */
/* Regra: NUNCA usar body ou * — qualquer herança chega nos spans de ícone    */
/* e quebra os ligatures Material Icons (ex: "arrow_right" vira texto literal) */

/* Texto corrido / Markdown */
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stText"],
[data-testid="stCaptionContainer"] {
    font-family: 'Barlow Condensed', 'Montserrat', 'Arial Narrow', sans-serif !important;
}

/* Labels de widgets */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label {
    font-family: 'Barlow Condensed', 'Montserrat', 'Arial Narrow', sans-serif !important;
}

/* Inputs, selects, textarea */
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea,
[data-baseweb="select"] div[role="combobox"],
[data-baseweb="select"] div[role="option"],
.stTextArea textarea,
[data-testid="stTextInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stNumberInput"] input {
    font-family: 'Barlow Condensed', 'Montserrat', 'Arial Narrow', sans-serif !important;
}

/* Botões */
[data-testid="baseButton-primary"],
[data-testid="baseButton-secondary"],
.stFormSubmitButton > button {
    font-family: 'Barlow Condensed', 'Montserrat', 'Arial Narrow', sans-serif !important;
}

/* Métricas */
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"],
[data-testid="stMetricDeltaIcon"] {
    font-family: 'Barlow Condensed', 'Montserrat', 'Arial Narrow', sans-serif !important;
}

/* Alertas / notificações */
[data-testid="stAlert"] p,
[data-testid="stAlert"] div[data-testid="stMarkdownContainer"] {
    font-family: 'Barlow Condensed', 'Montserrat', 'Arial Narrow', sans-serif !important;
}

/* Expander — só o label, não o ícone */
details > summary > div,
details > summary > p,
details > summary > span[data-testid] {
    font-family: 'Barlow Condensed', 'Montserrat', 'Arial Narrow', sans-serif !important;
}

/* Sidebar — apenas spans de texto, não ícones */
[data-testid="stSidebarNavLink"] p,
[data-testid="stSidebarNavLink"] span[data-testid],
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    font-family: 'Barlow Condensed', 'Montserrat', 'Arial Narrow', sans-serif !important;
}

/* Dataframe */
[data-testid="stDataFrame"] td,
[data-testid="stDataFrame"] th {
    font-family: 'Barlow Condensed', 'Montserrat', 'Arial Narrow', sans-serif !important;
}

/* ===== TIPOGRAFIA ===== */
h1, h2, h3, h4, h5, h6 {
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.03em !important;
    color: #FFFFFF !important;
}
p, span, li,
.stMarkdown p,
[data-testid="stMarkdownContainer"] p {
    color: rgba(255,255,255,0.88) !important;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060f14 0%, #091f2b 60%, #0d3340 100%) !important;
    border-right: 2px solid rgba(45,197,180,0.4) !important;
}
[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.88) !important;
}

/* Ícone de abrir sidebar (quando recolhida) */
[data-testid="stSidebarCollapsedControl"] button {
    background: linear-gradient(135deg, #0B2E3A, #1D7A8A) !important;
    border: 1px solid rgba(45,197,180,0.6) !important;
    border-radius: 0 8px 8px 0 !important;
    color: #2DC5B4 !important;
    box-shadow: 2px 0 12px rgba(45,197,180,0.25) !important;
}
[data-testid="stSidebarCollapsedControl"] button:hover {
    background: rgba(45,197,180,0.3) !important;
    box-shadow: 2px 0 20px rgba(45,197,180,0.45) !important;
}
[data-testid="stSidebarCollapsedControl"] button svg {
    fill: #2DC5B4 !important;
    stroke: #2DC5B4 !important;
}

/* Ícone de fechar sidebar (dentro da barra) */
[data-testid="stSidebarCollapseButton"] button {
    background: rgba(45,197,180,0.12) !important;
    border: 1px solid rgba(45,197,180,0.4) !important;
    border-radius: 8px !important;
    color: #2DC5B4 !important;
    transition: all 0.2s !important;
}
[data-testid="stSidebarCollapseButton"] button:hover {
    background: rgba(45,197,180,0.28) !important;
    border-color: #2DC5B4 !important;
}
[data-testid="stSidebarCollapseButton"] button svg {
    fill: #2DC5B4 !important;
    stroke: #2DC5B4 !important;
}

/* Nav links como botões */
[data-testid="stSidebarNavLink"] {
    display: flex !important;
    align-items: center !important;
    border-radius: 10px !important;
    margin: 4px 8px !important;
    padding: 0.65rem 1rem !important;
    background: rgba(45,197,180,0.06) !important;
    border: 1px solid rgba(45,197,180,0.18) !important;
    transition: all 0.2s !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
}
[data-testid="stSidebarNavLink"]:hover {
    background: rgba(45,197,180,0.22) !important;
    border-color: rgba(45,197,180,0.55) !important;
    transform: translateX(4px) !important;
    box-shadow: 2px 0 12px rgba(45,197,180,0.2) !important;
}
[data-testid="stSidebarNavLink"][aria-selected="true"],
[data-testid="stSidebarNavLink"].active {
    background: linear-gradient(135deg, rgba(45,197,180,0.28), rgba(26,128,144,0.28)) !important;
    border-color: #2DC5B4 !important;
    box-shadow: 0 0 12px rgba(45,197,180,0.2) !important;
}
[data-testid="stSidebarNavLink"] span,
[data-testid="stSidebarNavLink"] p {
    font-size: 1rem !important;
    font-weight: 700 !important;
}

/* ===== BOTÕES ===== */
[data-testid="baseButton-primary"],
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #2DC5B4 0%, #1A8090 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    box-shadow: 0 2px 8px rgba(45,197,180,0.35) !important;
    transition: all 0.2s !important;
}
[data-testid="baseButton-primary"]:hover,
.stFormSubmitButton > button:hover {
    box-shadow: 0 4px 16px rgba(45,197,180,0.5) !important;
    transform: translateY(-1px) !important;
}
[data-testid="baseButton-secondary"] {
    background: rgba(45,197,180,0.1) !important;
    color: #2DC5B4 !important;
    border: 1px solid rgba(45,197,180,0.55) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

/* ===== INPUTS ===== */
[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
.stTextArea textarea,
[data-testid="stTextInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stNumberInput"] input {
    background: rgba(11,46,58,0.85) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(45,197,180,0.4) !important;
    border-radius: 8px !important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within,
.stTextArea textarea:focus,
[data-testid="stTextInput"] input:focus {
    border-color: #2DC5B4 !important;
    box-shadow: 0 0 0 2px rgba(45,197,180,0.2) !important;
}
[data-baseweb="popover"] li,
[data-baseweb="menu"] li {
    background: #0B3040 !important;
    color: #FFFFFF !important;
}
[data-baseweb="popover"] li:hover,
[data-baseweb="menu"] li:hover {
    background: rgba(45,197,180,0.25) !important;
}
label[data-testid="stWidgetLabel"] > div {
    color: rgba(255,255,255,0.8) !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.05em !important;
}

/* ===== MÉTRICAS / KPIs ===== */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(45,197,180,0.4) !important;
    border-radius: 14px !important;
    padding: 1.1rem 1.25rem !important;
    backdrop-filter: blur(6px) !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(45,197,180,0.2) !important;
}
[data-testid="stMetricValue"] {
    color: #2DC5B4 !important;
    font-size: 2.4rem !important;
    font-weight: 800 !important;
}
[data-testid="stMetricLabel"] {
    color: rgba(255,255,255,0.65) !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    font-weight: 600 !important;
}

/* ===== CARDS / CONTAINERS BORDADOS (Kanban) ===== */
[data-testid="stVerticalBlockBorderWrapper"] > div > div {
    background: rgba(11,46,58,0.6) !important;
    border: 1px solid rgba(45,197,180,0.3) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(6px) !important;
    transition: box-shadow 0.2s !important;
}
[data-testid="stVerticalBlockBorderWrapper"] > div > div:hover {
    box-shadow: 0 4px 16px rgba(45,197,180,0.15) !important;
}

/* ===== EXPANDER ===== */
details {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(45,197,180,0.22) !important;
    border-radius: 10px !important;
}
details > summary {
    color: #2DC5B4 !important;
    font-weight: 700 !important;
    letter-spacing: 0.03em !important;
}

/* ===== FORMULÁRIO ===== */
[data-testid="stForm"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(45,197,180,0.2) !important;
    border-radius: 14px !important;
}

/* ===== DATAFRAME ===== */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid rgba(45,197,180,0.2) !important;
}

/* ===== FILE UPLOADER ===== */
[data-testid="stFileUploadDropzone"] {
    background: rgba(11,46,58,0.55) !important;
    border: 2px dashed rgba(45,197,180,0.5) !important;
    border-radius: 12px !important;
    padding: 1.25rem 1rem !important;
    text-align: center !important;
    transition: border-color 0.2s, background 0.2s !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: #2DC5B4 !important;
    background: rgba(45,197,180,0.08) !important;
}
[data-testid="stFileUploadDropzone"] * {
    color: rgba(255,255,255,0.75) !important;
}
[data-testid="stFileUploadDropzone"] button,
[data-testid="stFileUploaderDropzoneInstructions"] button,
[data-testid="baseButton-secondary"][kind="secondary"] {
    background: rgba(45,197,180,0.14) !important;
    border: 1px solid rgba(45,197,180,0.55) !important;
    border-radius: 8px !important;
    color: #2DC5B4 !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    padding: 0.35rem 1.1rem !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
}
[data-testid="stFileUploadDropzone"] button:hover {
    background: rgba(45,197,180,0.28) !important;
    border-color: #2DC5B4 !important;
    box-shadow: 0 0 10px rgba(45,197,180,0.25) !important;
}
[data-testid="stFileUploaderFile"] {
    background: rgba(45,197,180,0.08) !important;
    border: 1px solid rgba(45,197,180,0.3) !important;
    border-radius: 8px !important;
    padding: 0.4rem 0.75rem !important;
    margin-top: 0.5rem !important;
}

/* ===== DIVISOR ===== */
hr {
    border-color: rgba(45,197,180,0.25) !important;
    margin: 1.5rem 0 !important;
}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0B2E3A; }
::-webkit-scrollbar-thumb { background: #2DC5B4; border-radius: 3px; }

/* ===== UTILITÁRIOS ===== */
.badge-dias {
    display: inline-block;
    background: #2DC5B4;
    color: #FFFFFF !important;
    font-weight: 700;
    border-radius: 999px;
    padding: 3px 14px;
    font-size: 0.78rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.card-dias {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(45,197,180,0.35);
    border-radius: 14px;
    padding: 1.5rem;
    height: 100%;
    transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
}
.card-dias:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(45,197,180,0.2);
    border-color: rgba(45,197,180,0.6);
}
</style>
"""


def aplicar_tema():
    """Injeta identidade visual Dias+ no app Streamlit."""
    st.markdown(_CSS, unsafe_allow_html=True)
    _tentar_logo()


def _tentar_logo():
    base = os.path.dirname(os.path.abspath(__file__))
    for nome in ("logo-dias.png", "logo-dias.svg", "logo_dias.png"):
        caminho = os.path.join(base, "..", "assets", nome)
        if os.path.exists(caminho):
            try:
                st.logo(caminho)
            except Exception:
                try:
                    st.sidebar.image(caminho, use_container_width=True)
                except Exception:
                    pass
            return


def layout_plotly():
    """Retorna kwargs de layout para gráficos Plotly com tema Dias+."""
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(11,46,58,0.5)",
        font=dict(family="Barlow Condensed, Montserrat, sans-serif", color="#FFFFFF", size=13),
        title=dict(font=dict(family="Barlow Condensed, sans-serif", color="#FFFFFF", size=15)),
        xaxis=dict(
            gridcolor="rgba(45,197,180,0.12)",
            color="rgba(255,255,255,0.7)",
            linecolor="rgba(45,197,180,0.2)",
        ),
        yaxis=dict(
            gridcolor="rgba(45,197,180,0.12)",
            color="rgba(255,255,255,0.7)",
            linecolor="rgba(45,197,180,0.2)",
        ),
        margin=dict(t=40, l=10, r=10, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#FFFFFF")),
    )


PALETA_PLOTLY = ["#2DC5B4", "#5BA8B8", "#1A8090", "#C47A77", "#1A5A68", "#0B3040"]

# ===== CONSTANTES COMPARTILHADAS =====

# Lista completa de filiais (fonte: Contatos regionais-filiais)
OPCOES_FILIAIS = [
    # SP – Capital / Grande SP
    "Carapicuíba", "Guarulhos", "Osasco", "NASP",
    "São Bernardo do Campo", "São Mateus", "Taboão da Serra",
    "Barueri", "Cotia", "Diadema", "Embu das Artes",
    "Ferraz de Vasconcelos", "Itaquaquecetuba", "Mauá",
    "Mogi das Cruzes", "Santo André", "São Caetano do Sul",
    "Suzano",
    # SP – Litoral / Interior
    "Praia Grande", "Santos", "São Vicente", "Cubatão", "Guarujá",
    "Araçatuba", "Bauru", "Campinas", "Itapetininga",
    "Presidente Prudente", "Ribeirão Preto", "São José dos Campos",
    "Sorocaba",
    # RJ
    "Barra Mansa", "Campo Grande", "Campos dos Goytacazes",
    "Duque de Caxias", "Nova Friburgo", "São Gonçalo",
    "São Pedro da Aldeia",
    # PR
    "Curitiba", "Ponta Grossa",
]

OPCOES_CATEGORIAS = [
    "LTA / Alvará",
    "Manutenção de Frota",
    "Documentação",
    "Avaria / Falta",
    "Compras",
    "Serviços Gerais",
    "RH / Pessoal",
    "TI / Sistemas",
    "Outros",
]
