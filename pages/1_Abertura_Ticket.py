import streamlit as st
from datetime import datetime
import os

from database.conexao import SessionLocal
from database.operacoes_crud import criar_demanda
from utils.tema import aplicar_tema, verificar_sessao, logout_sidebar, OPCOES_FILIAIS, OPCOES_CATEGORIAS
from utils.notificacoes import disparar_notificacao_async, disparar_notificacao_setor_async, OPCOES_SETORES

st.set_page_config(page_title="Nova Demanda | Dias+", page_icon="📝", layout="centered")
aplicar_tema()
logout_sidebar()

st.markdown(
    """
    <div style="padding:1.5rem 0 0.75rem;">
        <div style="font-family:'Barlow Condensed',sans-serif; font-size:2.2rem; font-weight:900;
                    text-transform:uppercase; letter-spacing:0.04em; color:#FFFFFF; line-height:1.05;">
            ABERTURA DE <span style="color:#2DC5B4;">NOVA DEMANDA</span>
        </div>
        <p style="color:rgba(255,255,255,0.58); margin-top:0.4rem; font-size:0.95rem;">
            Preencha os dados abaixo para registrar uma nova solicitação no sistema logístico.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

usuario = verificar_sessao()

st.markdown(
    f"""
    <div style="display:flex; align-items:center; gap:0.75rem; padding:0.75rem 1rem;
                background:rgba(45,197,180,0.1); border:1px solid rgba(45,197,180,0.35);
                border-radius:10px; margin-bottom:1.25rem; flex-wrap:wrap;">
        <span style="font-size:1.4rem;">👤</span>
        <div>
            <span style="color:rgba(255,255,255,0.55); font-size:0.75rem; text-transform:uppercase;
                         letter-spacing:0.05em;">Operador</span><br>
            <strong style="color:#FFFFFF; font-size:1.05rem;">{usuario['nome']}</strong>
            <span style="color:rgba(255,255,255,0.35); margin:0 0.5rem;">|</span>
            <span style="color:rgba(255,255,255,0.65);">🏢 {usuario['filial_base']}</span>
        </div>
        <div style="margin-left:auto;">
            <span class="badge-dias">{usuario['nivel_acesso']}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("form_nova_demanda", clear_on_submit=True):

    col1, col2 = st.columns(2)

    with col1:
        index_filial = (
            OPCOES_FILIAIS.index(usuario["filial_base"])
            if usuario["filial_base"] in OPCOES_FILIAIS
            else 0
        )

        filial = st.selectbox(
            "Unidade/Filial de Origem *",
            options=OPCOES_FILIAIS,
            index=index_filial,
            disabled=(usuario["nivel_acesso"] == "Operacao"),
        )

        categoria = st.selectbox(
            "Categoria da Demanda *",
            OPCOES_CATEGORIAS,
        )

        setor_destino = st.selectbox(
            "Setor Destinatário *",
            OPCOES_SETORES,
            help="Setor responsável por tratar esta solicitação. Um e-mail será enviado automaticamente.",
        )

    with col2:
        prioridade = st.selectbox(
            "Nível de Prioridade *",
            ["Baixa", "Média", "Alta", "Crítica"],
        )

        prazo_desejado = st.date_input(
            "Prazo Desejado (Opcional)",
            value=None,
            min_value=datetime.today(),
        )

    descricao = st.text_area(
        "Descrição Detalhada *",
        placeholder="Descreva o problema, placa do veículo, número da nota fiscal ou licença pendente...",
        height=150,
    )

    anexos = st.file_uploader("Anexar Evidências (Opcional)", accept_multiple_files=True)

    st.markdown(
        "<small style='color:rgba(255,255,255,0.4);'>* Campos obrigatórios</small>",
        unsafe_allow_html=True,
    )

    btn_submit = st.form_submit_button("Gerar Ticket", type="primary", use_container_width=True)

_TIPOS_PERMITIDOS = {"pdf", "jpg", "jpeg", "png", "xlsx", "xls", "docx", "doc"}
_TAMANHO_MAX_MB   = 5

if btn_submit:
    erros_upload = []
    for arq in (anexos or []):
        ext = arq.name.rsplit(".", 1)[-1].lower() if "." in arq.name else ""
        if ext not in _TIPOS_PERMITIDOS:
            erros_upload.append(f"Tipo de arquivo não permitido: <b>.{ext}</b>")
        elif arq.size > _TAMANHO_MAX_MB * 1024 * 1024:
            erros_upload.append(f"<b>{arq.name}</b> excede o limite de {_TAMANHO_MAX_MB} MB")

    if erros_upload:
        for msg in erros_upload:
            st.error(msg)
    elif not descricao.strip():
        st.error("⚠️ A descrição detalhada é obrigatória!")
    else:
        with st.spinner("Registrando demanda no banco de dados..."):
            db = SessionLocal()
            try:
                nova_demanda = criar_demanda(
                    db=db,
                    solicitante_id=usuario["id"],
                    filial=filial,
                    categoria=categoria,
                    prioridade=prioridade,
                    descricao=descricao,
                    prazo=prazo_desejado,
                    setor_destino=setor_destino,
                )

                if nova_demanda:
                    if anexos:
                        os.makedirs("uploads", exist_ok=True)
                        for arquivo in anexos:
                            caminho_arquivo = os.path.join(
                                "uploads", f"{nova_demanda.id_ticket}_{arquivo.name}"
                            )
                            with open(caminho_arquivo, "wb") as f:
                                f.write(arquivo.getbuffer())

                    disparar_notificacao_async(nova_demanda, usuario["nome"])
                    disparar_notificacao_setor_async(nova_demanda, usuario["nome"])

                    st.success(
                        f"✅ Demanda registrada com sucesso! **Ticket: {nova_demanda.id_ticket}**  \n"
                        f"📧 Setor *{nova_demanda.setor_destino}* foi notificado por e-mail."
                    )
                    st.balloons()
                else:
                    st.error("❌ Falha ao registrar demanda no banco de dados. Tente novamente.")

            except Exception as e:
                st.error(f"Ocorreu um erro inesperado: {e}")
            finally:
                db.close()
