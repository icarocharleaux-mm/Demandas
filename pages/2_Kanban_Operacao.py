import streamlit as st
from datetime import datetime

from database.conexao import SessionLocal
from database.operacoes_crud import atualizar_status_demanda, atualizar_setor_demanda, listar_demandas_por_filial
from utils.tema import aplicar_tema, verificar_sessao, logout_sidebar, OPCOES_FILIAIS
from utils.notificacoes import disparar_notificacao_setor_async, OPCOES_SETORES

st.set_page_config(page_title="Kanban | Dias+", page_icon="📋", layout="wide")
aplicar_tema()
logout_sidebar()
usuario = verificar_sessao()

st.markdown(
    """
    <div style="padding:1.5rem 0 0.75rem;">
        <div style="font-family:'Barlow Condensed',sans-serif; font-size:2.2rem; font-weight:900;
                    text-transform:uppercase; letter-spacing:0.04em; color:#FFFFFF; line-height:1.05;">
            QUADRO KANBAN — <span style="color:#2DC5B4;">GESTÃO DE DEMANDAS</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

col_filtro1, _ = st.columns([2, 4])

with col_filtro1:
    if usuario["nivel_acesso"] in ["Gestor", "Admin"]:
        filial_selecionada = st.selectbox(
            "Filtrar por Filial",
            ["Todas"] + OPCOES_FILIAIS,
        )
        filtro_db = None if filial_selecionada == "Todas" else filial_selecionada
    else:
        st.markdown(
            f"""
            <div style="padding:0.6rem 1rem; background:rgba(45,197,180,0.1);
                        border:1px solid rgba(45,197,180,0.35); border-radius:8px;
                        font-size:0.9rem; color:rgba(255,255,255,0.8);">
                📍 Exibindo demandas restritas à unidade:
                <strong style="color:#2DC5B4;">{usuario['filial_base']}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
        filtro_db = usuario["filial_base"]

db = SessionLocal()
try:
    demandas_brutas = listar_demandas_por_filial(db, filtro_db)
finally:
    db.close()

CORES_PRIORIDADE = {
    "Crítica": "🔴",
    "Alta":    "🟠",
    "Média":   "🟡",
    "Baixa":   "🟢",
}

# Cor da borda esquerda e ícone para cada coluna
CORES_STATUS = {
    "Novo":               ("#2DC5B4", "🆕"),
    "Em análise":         ("#5BA8B8", "🔍"),
    "Em andamento":       ("#1A8090", "⚙️"),
    "Pendente terceiros": ("#C47A77", "⏳"),
    "Finalizado":         ("#4dbe8c", "✅"),
}

colunas_kanban = {s: [] for s in CORES_STATUS}

for d in demandas_brutas:
    status_seguro = d.status if d.status in colunas_kanban else "Novo"
    colunas_kanban[status_seguro].append(d)

st.markdown("<br>", unsafe_allow_html=True)
cols = st.columns(len(colunas_kanban))

for index, (nome_status, lista_tickets) in enumerate(colunas_kanban.items()):
    with cols[index]:
        cor, icone_col = CORES_STATUS[nome_status]
        st.markdown(
            f"""
            <div style="border-left:4px solid {cor}; padding:0.4rem 0.75rem; margin-bottom:0.75rem;
                        background:rgba(255,255,255,0.05); border-radius:0 8px 8px 0;">
                <span style="font-family:'Barlow Condensed',sans-serif; font-size:0.92rem; font-weight:800;
                             text-transform:uppercase; letter-spacing:0.04em; color:{cor};">
                    {icone_col} {nome_status}
                </span>
                <span style="background:{cor}; color:#FFFFFF; border-radius:999px; padding:1px 9px;
                             font-size:0.7rem; font-weight:700; margin-left:0.5rem;">
                    {len(lista_tickets)}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for ticket in lista_tickets:
            with st.container(border=True):
                icone_pri = CORES_PRIORIDADE.get(ticket.prioridade, "⚪")

                st.markdown(f"**{ticket.id_ticket}**")
                st.caption(f"{icone_pri} {ticket.prioridade} · 📂 {ticket.categoria}")
                st.write(f"🏢 {ticket.filial_origem}")

                if ticket.prazo:
                    hoje = datetime.now().date()
                    if ticket.status != "Finalizado" and ticket.prazo.date() < hoje:
                        st.error(f"⚠️ Atrasado — Prazo: {ticket.prazo.strftime('%d/%m/%Y')}")
                    else:
                        st.info(f"⏳ Prazo: {ticket.prazo.strftime('%d/%m/%Y')}")

                with st.expander("Ações e Atualização"):
                    st.write(f"**Descrição:** {ticket.descricao[:100]}...")
                    if ticket.setor_destino:
                        st.caption(f"📬 Setor atual: **{ticket.setor_destino}**")

                    with st.form(key=f"form_{ticket.id_ticket}"):
                        novo_status = st.selectbox(
                            "Mover para:",
                            list(colunas_kanban.keys()),
                            index=list(colunas_kanban.keys()).index(ticket.status),
                        )
                        comentario = st.text_input(
                            "Comentário (opcional)", placeholder="Ex: Faltou documento X"
                        )
                        btn_salvar = st.form_submit_button(
                            "Atualizar Status", use_container_width=True
                        )

                        if btn_salvar:
                            db_update = SessionLocal()
                            try:
                                sucesso, msg = atualizar_status_demanda(
                                    db=db_update,
                                    id_ticket=ticket.id_ticket,
                                    usuario_id=usuario["id"],
                                    novo_status=novo_status,
                                    comentario_acao=comentario,
                                )
                                if sucesso:
                                    st.success("Atualizado! Recarregando...")
                                    st.rerun()
                                else:
                                    st.warning(msg)
                            finally:
                                db_update.close()

                    if usuario["nivel_acesso"] in ("Gestor", "Admin"):
                        with st.form(key=f"form_setor_{ticket.id_ticket}"):
                            st.markdown(
                                "<small style='color:rgba(255,255,255,0.5);text-transform:uppercase;"
                                "letter-spacing:0.05em;font-size:0.7rem;'>Reatribuir para outro setor</small>",
                                unsafe_allow_html=True,
                            )
                            idx_setor = (
                                OPCOES_SETORES.index(ticket.setor_destino)
                                if ticket.setor_destino in OPCOES_SETORES
                                else 0
                            )
                            novo_setor = st.selectbox("Novo setor:", OPCOES_SETORES, index=idx_setor)
                            motivo = st.text_input("Motivo da reatribuição", placeholder="Ex: Encaminhado ao setor correto")
                            btn_reatribuir = st.form_submit_button("Reatribuir", use_container_width=True)

                            if btn_reatribuir:
                                if novo_setor == ticket.setor_destino:
                                    st.warning("O setor selecionado já é o atual.")
                                else:
                                    db_setor = SessionLocal()
                                    try:
                                        sucesso, msg = atualizar_setor_demanda(
                                            db=db_setor,
                                            id_ticket=ticket.id_ticket,
                                            usuario_id=usuario["id"],
                                            novo_setor=novo_setor,
                                            comentario=motivo,
                                        )
                                        if sucesso:
                                            ticket.setor_destino = novo_setor
                                            disparar_notificacao_setor_async(ticket, usuario["nome"])
                                            st.success(f"Reatribuído para {novo_setor}! Setor notificado por e-mail.")
                                            st.rerun()
                                        else:
                                            st.warning(msg)
                                    finally:
                                        db_setor.close()
