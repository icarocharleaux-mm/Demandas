import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

from database.conexao import engine
from utils.tema import aplicar_tema, verificar_sessao, logout_sidebar, layout_plotly, PALETA_PLOTLY

st.set_page_config(page_title="Painel Gerencial | Dias+", page_icon="📊", layout="wide")
aplicar_tema()
logout_sidebar()
_usuario = verificar_sessao()

if _usuario["nivel_acesso"] not in ("Gestor", "Admin"):
    st.markdown(
        """
        <div style="padding:1.25rem 1.5rem; background:rgba(196,122,119,0.12);
                    border:1px solid rgba(196,122,119,0.45); border-radius:10px; margin-top:1rem;">
            <div style="font-size:1.1rem; font-weight:800; color:#C47A77;
                         text-transform:uppercase; letter-spacing:0.04em;">
                ⛔ Acesso Restrito
            </div>
            <div style="color:rgba(255,255,255,0.6); font-size:0.9rem; margin-top:0.4rem;">
                Esta área é exclusiva para <strong>Gestores</strong> e <strong>Administradores</strong>.
                Entre em contato com seu gestor para solicitar acesso.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

st.markdown(
    """
    <div style="padding:1.5rem 0 0.75rem;">
        <div style="font-family:'Barlow Condensed',sans-serif; font-size:2.2rem; font-weight:900;
                    text-transform:uppercase; letter-spacing:0.04em; color:#FFFFFF; line-height:1.05;">
            PAINEL INTEGRADO DE LOGÍSTICA — <span style="color:#2DC5B4;">VISÃO GERENCIAL</span>
        </div>
        <p style="color:rgba(255,255,255,0.58); margin-top:0.4rem; font-size:0.95rem;">
            Acompanhamento de volumetria, gargalos e SLAs das filiais.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=60)
def carregar_dados():
    df = pd.read_sql("SELECT * FROM demandas", engine)

    if df.empty:
        return df

    df["data_abertura"] = pd.to_datetime(df["data_abertura"])
    df["prazo"] = pd.to_datetime(df["prazo"])

    hoje = pd.to_datetime(datetime.now().date())

    df["atrasado"] = (df["status"] != "Finalizado") & (df["prazo"] < hoje)

    df["dias_uteis_aberto"] = df.apply(
        lambda row: np.busday_count(row["data_abertura"].date(), hoje.date())
        if row["status"] != "Finalizado"
        else 0,
        axis=1,
    )

    return df


df_demandas = carregar_dados()

if df_demandas.empty:
    st.info("Nenhuma demanda registrada no sistema ainda.")
else:
    # --- KPIs ---
    total_tickets = len(df_demandas)
    tickets_abertos = len(df_demandas[df_demandas["status"] != "Finalizado"])
    tickets_atrasados = len(df_demandas[df_demandas["atrasado"] == True])
    max_dias = df_demandas["dias_uteis_aberto"].max()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Demandas", total_tickets)
    col2.metric("Tickets em Andamento", tickets_abertos)
    col3.metric("Demandas Atrasadas", tickets_atrasados, delta_color="inverse")
    col4.metric("Ticket Mais Antigo (Dias Úteis)", max_dias)

    st.markdown("---")

    # --- Gráficos ---
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.markdown(
            """
            <div style="font-family:'Barlow Condensed',sans-serif; font-size:1.2rem; font-weight:800;
                        text-transform:uppercase; color:#FFFFFF; letter-spacing:0.04em; margin-bottom:0.25rem;">
                FUNIL DE <span style="color:#2DC5B4;">STATUS</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        df_status = df_demandas["status"].value_counts().reset_index()
        df_status.columns = ["Status", "Quantidade"]

        fig_status = px.bar(
            df_status,
            x="Status",
            y="Quantidade",
            color="Status",
            text_auto=True,
            color_discrete_sequence=PALETA_PLOTLY,
        )
        fig_status.update_layout(showlegend=False, **layout_plotly())
        fig_status.update_traces(marker_line_width=0)
        st.plotly_chart(fig_status, use_container_width=True)

    with col_g2:
        st.markdown(
            """
            <div style="font-family:'Barlow Condensed',sans-serif; font-size:1.2rem; font-weight:800;
                        text-transform:uppercase; color:#FFFFFF; letter-spacing:0.04em; margin-bottom:0.25rem;">
                DEMANDAS POR FILIAL E <span style="color:#2DC5B4;">CATEGORIA</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        df_filial_cat = (
            df_demandas.groupby(["filial_origem", "categoria"]).size().reset_index(name="Quantidade")
        )

        fig_filial = px.bar(
            df_filial_cat,
            x="filial_origem",
            y="Quantidade",
            color="categoria",
            barmode="stack",
            color_discrete_sequence=PALETA_PLOTLY,
        )
        fig_filial.update_layout(**layout_plotly())
        fig_filial.update_traces(marker_line_width=0)
        st.plotly_chart(fig_filial, use_container_width=True)

    st.markdown("---")

    # --- Tabela de atenção imediata ---
    st.markdown(
        """
        <div style="font-family:'Barlow Condensed',sans-serif; font-size:1.2rem; font-weight:800;
                    text-transform:uppercase; color:#FFFFFF; letter-spacing:0.04em; margin-bottom:0.75rem;">
            ⚠️ ATENÇÃO IMEDIATA — <span style="color:#C47A77;">TICKETS ATRASADOS OU CRÍTICOS</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df_criticos = df_demandas[
        ((df_demandas["prioridade"] == "Crítica") | (df_demandas["atrasado"] == True))
        & (df_demandas["status"] != "Finalizado")
    ]

    if not df_criticos.empty:
        colunas_exibicao = ["id_ticket", "filial_origem", "categoria", "status", "dias_uteis_aberto"]
        st.dataframe(
            df_criticos[colunas_exibicao].sort_values(by="dias_uteis_aberto", ascending=False),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.success("Nenhum ticket crítico ou em atraso no momento! 🎉")
