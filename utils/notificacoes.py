import os
import smtplib
import threading
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

from database.conexao import SessionLocal, Demanda

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.office365.com")
SMTP_PORT   = int(os.getenv("SMTP_PORT", 587))
SMTP_USER   = os.getenv("SMTP_USER", "seu_email_corporativo@dominio.com.br")
SMTP_PASS   = os.getenv("SMTP_PASS", "sua_senha")

# ============================================================
# ROTEAMENTO POR FILIAL — Fonte: Contatos regionais-filiais
# Gestor = responsável da filial | RT = responsável técnico
# ============================================================
MAPA_FILIAL_CONTATOS = {
    # SP – Capital / Grande SP
    "Carapicuíba":        {"gestor": "alexandre.chagas@mmdeliverytransportes.com.br",  "rt": "flavio.santos@mmdeliverytransportes.com.br"},
    "Guarulhos":          {"gestor": "Marcio.rollo@diaslog.com.br",                     "rt": "robison.lima@mddelivery.com.br"},
    "Osasco":             {"gestor": "gilvan.oliveira@mmdeliverytransportes.com.br",    "rt": "flavio.santos@mmdeliverytransportes.com.br"},
    "NASP":               {"gestor": "Lucas.oliveira@mmdeliverytransportes.com.br",     "rt": None},
    "São Bernardo do Campo": {"gestor": "alex.peres@mmdeliverytransportes.com.br",      "rt": "icaro.nascimento@mmdeliverytransportes.com.br"},
    "São Bernardo":       {"gestor": "alex.peres@mmdeliverytransportes.com.br",         "rt": "icaro.nascimento@mmdeliverytransportes.com.br"},
    "São Mateus":         {"gestor": "Marcio.rollo@diaslog.com.br",                     "rt": None},
    "São Matheus":        {"gestor": "Marcio.rollo@diaslog.com.br",                     "rt": None},
    "Taboão da Serra":    {"gestor": "alexandre.chagas@mmdeliverytransportes.com.br",   "rt": "flavio.santos@mmdeliverytransportes.com.br"},
    # SP – Litoral / Interior
    "Praia Grande":       {"gestor": "alex.peres@mmdeliverytransportes.com.br",         "rt": "icaro.nascimento@mmdeliverytransportes.com.br"},
    "Araçatuba":          {"gestor": "wilton.silva@mmdeliverytransportes.com.br",       "rt": "Yago.Fernando@mmdeliverytransportes.com.br"},
    "Bauru":              {"gestor": "wilton.silva@mmdeliverytransportes.com.br",       "rt": "Yago.Fernando@mmdeliverytransportes.com.br"},
    "Campinas":           {"gestor": "leandro.silva@mddelivery.com.br",                 "rt": "robison.lima@mddelivery.com.br"},
    "Itapetininga":       {"gestor": "leandro.silva@mddelivery.com.br",                 "rt": "robison.lima@mddelivery.com.br"},
    "Presidente Prudente":{"gestor": "wilton.silva@mmdeliverytransportes.com.br",       "rt": "Yago.Fernando@mmdeliverytransportes.com.br"},
    "Ribeirão Preto":     {"gestor": "wilton.silva@mmdeliverytransportes.com.br",       "rt": "antenor.hugo@mddelivery.com.br"},
    "São José dos Campos":{"gestor": "rodrigo.rodrigues@mmdeliverytransportes.com.br",  "rt": "andressa.ramires@mmdeliverytransportes.com.br"},
    # RJ
    "Barra Mansa":           {"gestor": "helder.rodrigues@mddelivery.com.br", "rt": "leonardo.oliveira@mddelivery.com.br"},
    "Campo Grande":          {"gestor": "helder.rodrigues@mddelivery.com.br", "rt": "leonardo.oliveira@mddelivery.com.br"},
    "Campos dos Goytacazes": {"gestor": "helder.rodrigues@mddelivery.com.br", "rt": "sara.souza@mddelivery.com.br"},
    "Duque de Caxias":       {"gestor": "laerte.martins@mddelivery.com.br",   "rt": "leonardo.oliveira@mddelivery.com.br"},
    "Nova Friburgo":         {"gestor": "helder.rodrigues@mddelivery.com.br", "rt": "sara.souza@mddelivery.com.br"},
    "São Gonçalo":           {"gestor": "helder.rodrigues@mddelivery.com.br", "rt": "arthur.rodrigues@mddelivery.com.br"},
    "São Pedro da Aldeia":   {"gestor": "helder.rodrigues@mddelivery.com.br", "rt": "arthur.rodrigues@mddelivery.com.br"},
    # PR
    "Curitiba":     {"gestor": "jefferson.marques@fastty.com.br", "rt": "sandy.mara@fastty.com.br"},
    "Ponta Grossa": {"gestor": "jefferson.marques@fastty.com.br", "rt": "sandy.mara@fastty.com.br"},
}

# CC automático em tickets Críticos → gerente regional da filial
# SPC = SP Capital (Edson) | SPI = SP Interior (Wilton) | RJ (Helder) | PR (Jefferson)
_GERENTE_REGIONAL: dict[str, str] = {
    # SP Capital
    "Carapicuíba":        "edson.silva@mmdeliverytransportes.com.br",
    "Guarulhos":          "edson.silva@mmdeliverytransportes.com.br",
    "Osasco":             "edson.silva@mmdeliverytransportes.com.br",
    "NASP":               "edson.silva@mmdeliverytransportes.com.br",
    "São Bernardo do Campo": "edson.silva@mmdeliverytransportes.com.br",
    "São Bernardo":       "edson.silva@mmdeliverytransportes.com.br",
    "São Mateus":         "edson.silva@mmdeliverytransportes.com.br",
    "São Matheus":        "edson.silva@mmdeliverytransportes.com.br",
    "Taboão da Serra":    "edson.silva@mmdeliverytransportes.com.br",
    # SP Interior
    "Praia Grande":        "wilton.silva@mmdeliverytransportes.com.br",
    "Araçatuba":           "wilton.silva@mmdeliverytransportes.com.br",
    "Bauru":               "wilton.silva@mmdeliverytransportes.com.br",
    "Campinas":            "wilton.silva@mmdeliverytransportes.com.br",
    "Itapetininga":        "wilton.silva@mmdeliverytransportes.com.br",
    "Presidente Prudente": "wilton.silva@mmdeliverytransportes.com.br",
    "Ribeirão Preto":      "wilton.silva@mmdeliverytransportes.com.br",
    "São José dos Campos": "wilton.silva@mmdeliverytransportes.com.br",
    # RJ
    "Barra Mansa":           "helder.rodrigues@mddelivery.com.br",
    "Campo Grande":          "helder.rodrigues@mddelivery.com.br",
    "Campos dos Goytacazes": "helder.rodrigues@mddelivery.com.br",
    "Duque de Caxias":       "helder.rodrigues@mddelivery.com.br",
    "Nova Friburgo":         "helder.rodrigues@mddelivery.com.br",
    "São Gonçalo":           "helder.rodrigues@mddelivery.com.br",
    "São Pedro da Aldeia":   "helder.rodrigues@mddelivery.com.br",
    # PR
    "Curitiba":     "jefferson.marques@fastty.com.br",
    "Ponta Grossa": "jefferson.marques@fastty.com.br",
}

# Fallback quando a filial não estiver no mapa
EMAIL_FALLBACK = "gestao@diaslog.com.br"


# ============================================================
# HELPERS DE ENVIO SMTP
# ============================================================
def _conectar_smtp() -> smtplib.SMTP:
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASS)
    return server


def _enviar(msg: MIMEMultipart) -> None:
    server = _conectar_smtp()
    server.send_message(msg)
    server.quit()


# ============================================================
# FUNÇÃO 1 — Novo ticket criado
# Disparada logo após criar_demanda() com sucesso
# ============================================================
def enviar_email_novo_ticket(ticket: Demanda, nome_solicitante: str) -> None:
    """Notifica gestor + RT da filial sobre novo ticket. CC ao gerente regional se Crítico."""

    # Roteamento por filial (gestor + RT)
    contatos      = MAPA_FILIAL_CONTATOS.get(ticket.filial_origem, {})
    email_gestor  = contatos.get("gestor") or EMAIL_FALLBACK
    email_rt      = contatos.get("rt")
    destinatarios = list(dict.fromkeys(filter(None, [email_gestor, email_rt])))  # dedup, preserva ordem

    # CC ao gerente regional somente para tickets Críticos
    email_cc = None
    if ticket.prioridade == "Crítica":
        gerente = _GERENTE_REGIONAL.get(ticket.filial_origem)
        if gerente and gerente not in destinatarios:
            email_cc = gerente

    prazo_str    = ticket.prazo.strftime("%d/%m/%Y") if ticket.prazo else "Não definido"
    abertura_str = ticket.data_abertura.strftime("%d/%m/%Y %H:%M") if ticket.data_abertura else "—"

    cores_prioridade = {
        "Crítica": "#C47A77",
        "Alta":    "#e08c3b",
        "Média":   "#c9a227",
        "Baixa":   "#2DC5B4",
    }
    cor_prioridade = cores_prioridade.get(ticket.prioridade, "#5BA8B8")

    tag_critico = " 🔴 CRÍTICO" if ticket.prioridade == "Crítica" else ""

    msg = MIMEMultipart("alternative")
    msg["From"]    = SMTP_USER
    msg["To"]      = ", ".join(destinatarios)
    msg["Subject"] = f"[Dias+]{tag_critico} Novo Ticket {ticket.id_ticket} — {ticket.filial_origem}"
    if email_cc:
        msg["Cc"] = email_cc

    corpo_html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f4f6f8;font-family:'Segoe UI',Arial,sans-serif;">

  <!-- WRAPPER -->
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f8;padding:32px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;border-radius:14px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.12);">

        <!-- HEADER DIAS+ -->
        <tr>
          <td style="background:linear-gradient(135deg,#0B2E3A 0%,#1D7A8A 100%);padding:28px 32px;">
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td>
                  <span style="font-family:'Segoe UI',Arial,sans-serif;font-size:26px;font-weight:900;
                               text-transform:uppercase;letter-spacing:2px;color:#FFFFFF;">DIAS</span>
                  <span style="font-size:26px;font-weight:900;color:#2DC5B4;">+</span>
                  <div style="font-size:11px;color:rgba(255,255,255,0.55);letter-spacing:3px;
                              text-transform:uppercase;margin-top:2px;">Central de Demandas</div>
                </td>
                <td align="right">
                  <span style="background:#2DC5B4;color:#FFFFFF;font-weight:700;border-radius:999px;
                               padding:5px 16px;font-size:12px;letter-spacing:1px;text-transform:uppercase;">
                    NOVO TICKET
                  </span>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- CORPO -->
        <tr>
          <td style="background:#FFFFFF;padding:28px 32px;">

            <p style="margin:0 0 20px;font-size:15px;color:#4a5568;">
              Um novo ticket foi aberto por <strong style="color:#0B3040;">{nome_solicitante}</strong>
              e requer sua atenção.
            </p>

            <!-- TICKET ID DESTAQUE -->
            <div style="background:linear-gradient(135deg,#0B2E3A,#1D7A8A);border-radius:10px;
                        padding:16px 20px;margin-bottom:20px;">
              <div style="font-size:11px;color:rgba(255,255,255,0.6);text-transform:uppercase;
                          letter-spacing:2px;margin-bottom:4px;">ID do Ticket</div>
              <div style="font-size:22px;font-weight:900;color:#2DC5B4;letter-spacing:1px;">
                {ticket.id_ticket}
              </div>
            </div>

            <!-- TABELA DE DETALHES -->
            <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;margin-bottom:20px;">
              <tr>
                <td style="padding:10px 14px;background:#f8fafc;border-bottom:1px solid #e2e8f0;
                            font-size:12px;color:#718096;text-transform:uppercase;letter-spacing:1px;
                            width:38%;font-weight:600;">
                  Filial
                </td>
                <td style="padding:10px 14px;background:#f8fafc;border-bottom:1px solid #e2e8f0;
                            font-size:14px;color:#0B3040;font-weight:600;">
                  {ticket.filial_origem}
                </td>
              </tr>
              <tr>
                <td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;
                            font-size:12px;color:#718096;text-transform:uppercase;letter-spacing:1px;font-weight:600;">
                  Categoria
                </td>
                <td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;
                            font-size:14px;color:#0B3040;">
                  {ticket.categoria}
                </td>
              </tr>
              <tr>
                <td style="padding:10px 14px;background:#f8fafc;border-bottom:1px solid #e2e8f0;
                            font-size:12px;color:#718096;text-transform:uppercase;letter-spacing:1px;font-weight:600;">
                  Prioridade
                </td>
                <td style="padding:10px 14px;background:#f8fafc;border-bottom:1px solid #e2e8f0;">
                  <span style="background:{cor_prioridade};color:#FFFFFF;font-weight:700;border-radius:999px;
                               padding:3px 12px;font-size:12px;letter-spacing:0.5px;">
                    {ticket.prioridade}
                  </span>
                </td>
              </tr>
              <tr>
                <td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;
                            font-size:12px;color:#718096;text-transform:uppercase;letter-spacing:1px;font-weight:600;">
                  Prazo Desejado
                </td>
                <td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;
                            font-size:14px;color:#0B3040;">
                  {prazo_str}
                </td>
              </tr>
              <tr>
                <td style="padding:10px 14px;background:#f8fafc;
                            font-size:12px;color:#718096;text-transform:uppercase;letter-spacing:1px;font-weight:600;">
                  Abertura
                </td>
                <td style="padding:10px 14px;background:#f8fafc;font-size:14px;color:#0B3040;">
                  {abertura_str}
                </td>
              </tr>
            </table>

            <!-- DESCRIÇÃO -->
            <div style="background:#f0faf9;border-left:4px solid #2DC5B4;border-radius:0 8px 8px 0;
                        padding:14px 16px;margin-bottom:24px;">
              <div style="font-size:11px;color:#2DC5B4;text-transform:uppercase;letter-spacing:1.5px;
                          font-weight:700;margin-bottom:6px;">Descrição</div>
              <div style="font-size:14px;color:#4a5568;line-height:1.6;">{ticket.descricao}</div>
            </div>

            <!-- CTA -->
            <div style="text-align:center;margin-bottom:8px;">
              <a href="#"
                 style="display:inline-block;background:linear-gradient(135deg,#2DC5B4,#1A8090);
                        color:#FFFFFF;font-weight:700;text-decoration:none;border-radius:8px;
                        padding:12px 32px;font-size:13px;letter-spacing:1px;text-transform:uppercase;">
                Acessar Kanban Operacional
              </a>
            </div>

          </td>
        </tr>

        <!-- FOOTER -->
        <tr>
          <td style="background:#0B3040;padding:16px 32px;text-align:center;">
            <div style="font-size:11px;color:rgba(255,255,255,0.45);letter-spacing:1px;">
              Mensagem automática · Central de Demandas Dias+ · diaslog.com.br
            </div>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>

</body>
</html>
"""

    msg.attach(MIMEText(corpo_html, "html", "utf-8"))

    try:
        _enviar(msg)
        print(f"[EMAIL] Novo ticket {ticket.id_ticket} notificado → {email_destino}")
    except Exception as e:
        print(f"[EMAIL] Falha ao notificar novo ticket {ticket.id_ticket}: {e}")


def disparar_notificacao_async(ticket: Demanda, nome_solicitante: str) -> None:
    """Envia o e-mail em thread separada para não bloquear o Streamlit."""
    t = threading.Thread(
        target=enviar_email_novo_ticket,
        args=(ticket, nome_solicitante),
        daemon=True,
    )
    t.start()


# ============================================================
# FUNÇÃO 2 — SLA vencido (varredura periódica, já existia)
# ============================================================
def enviar_email_alerta(ticket: Demanda) -> None:
    """Notifica sobre ticket com SLA estourado (chamada pelo job agendado)."""

    email_destino = MAPA_RESPONSAVEIS.get(ticket.categoria, EMAIL_FALLBACK)
    prazo_str     = ticket.prazo.strftime("%d/%m/%Y") if ticket.prazo else "—"

    msg = MIMEMultipart("alternative")
    msg["From"]    = SMTP_USER
    msg["To"]      = email_destino
    msg["Subject"] = f"[Dias+] ⚠️ SLA Vencido — {ticket.id_ticket} / {ticket.filial_origem}"

    corpo_html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f4f6f8;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f8;padding:32px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0"
             style="max-width:600px;border-radius:14px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.12);">
        <tr>
          <td style="background:linear-gradient(135deg,#0B2E3A 0%,#1D7A8A 100%);padding:28px 32px;">
            <span style="font-size:24px;font-weight:900;text-transform:uppercase;color:#FFFFFF;letter-spacing:2px;">DIAS</span>
            <span style="font-size:24px;font-weight:900;color:#2DC5B4;">+</span>
            <span style="float:right;background:#C47A77;color:#FFFFFF;font-weight:700;border-radius:999px;
                         padding:5px 16px;font-size:12px;text-transform:uppercase;letter-spacing:1px;">
              SLA VENCIDO
            </span>
          </td>
        </tr>
        <tr>
          <td style="background:#FFFFFF;padding:28px 32px;">
            <p style="font-size:15px;color:#4a5568;margin:0 0 20px;">
              O ticket <strong style="color:#C47A77;">{ticket.id_ticket}</strong> está com prazo vencido
              e ainda não foi finalizado.
            </p>
            <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;margin-bottom:20px;">
              <tr>
                <td style="padding:10px 14px;background:#f8fafc;border-bottom:1px solid #e2e8f0;
                            font-size:12px;color:#718096;text-transform:uppercase;letter-spacing:1px;font-weight:600;width:38%;">
                  Filial</td>
                <td style="padding:10px 14px;background:#f8fafc;border-bottom:1px solid #e2e8f0;
                            font-size:14px;color:#0B3040;font-weight:600;">
                  {ticket.filial_origem}</td>
              </tr>
              <tr>
                <td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;
                            font-size:12px;color:#718096;text-transform:uppercase;letter-spacing:1px;font-weight:600;">
                  Categoria</td>
                <td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;font-size:14px;color:#0B3040;">
                  {ticket.categoria} · {ticket.prioridade}</td>
              </tr>
              <tr>
                <td style="padding:10px 14px;background:#f8fafc;border-bottom:1px solid #e2e8f0;
                            font-size:12px;color:#718096;text-transform:uppercase;letter-spacing:1px;font-weight:600;">
                  Prazo original</td>
                <td style="padding:10px 14px;background:#f8fafc;border-bottom:1px solid #e2e8f0;
                            font-size:14px;color:#C47A77;font-weight:700;">
                  {prazo_str}</td>
              </tr>
              <tr>
                <td style="padding:10px 14px;font-size:12px;color:#718096;
                            text-transform:uppercase;letter-spacing:1px;font-weight:600;">
                  Status</td>
                <td style="padding:10px 14px;font-size:14px;color:#0B3040;">
                  {ticket.status}</td>
              </tr>
            </table>
            <div style="background:#f0faf9;border-left:4px solid #2DC5B4;border-radius:0 8px 8px 0;
                        padding:14px 16px;">
              <div style="font-size:11px;color:#2DC5B4;text-transform:uppercase;letter-spacing:1.5px;
                          font-weight:700;margin-bottom:6px;">Descrição</div>
              <div style="font-size:14px;color:#4a5568;line-height:1.6;">{ticket.descricao}</div>
            </div>
          </td>
        </tr>
        <tr>
          <td style="background:#0B3040;padding:16px 32px;text-align:center;">
            <div style="font-size:11px;color:rgba(255,255,255,0.45);letter-spacing:1px;">
              Alerta automático de SLA · Dias+ · diaslog.com.br
            </div>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>
"""

    msg.attach(MIMEText(corpo_html, "html", "utf-8"))

    try:
        _enviar(msg)
        print(f"[EMAIL] Alerta SLA enviado para {ticket.id_ticket}")
    except Exception as e:
        print(f"[EMAIL] Falha no alerta SLA {ticket.id_ticket}: {e}")


def varrer_base_e_notificar() -> None:
    """Varre o banco em busca de tickets com SLA vencido e dispara alertas."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando varredura de SLAs...")
    db = SessionLocal()
    try:
        hoje = datetime.now()
        tickets_atrasados = db.query(Demanda).filter(
            Demanda.status != "Finalizado",
            Demanda.prazo < hoje,
        ).all()

        if not tickets_atrasados:
            print("Nenhum ticket atrasado encontrado.")
            return

        for ticket in tickets_atrasados:
            enviar_email_alerta(ticket)

    finally:
        db.close()
        print("Varredura concluída.")


if __name__ == "__main__":
    varrer_base_e_notificar()
