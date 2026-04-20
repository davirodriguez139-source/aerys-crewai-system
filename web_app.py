from __future__ import annotations

import queue
import re
import threading
import time
from datetime import date
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from main import PROJECT_ROOT, save_output, validate_env
from src.crew import AerysCrewSystem
from src.database import (
    create_campaign,
    get_all_campaigns,
    get_campaign_by_id,
    update_campaign_status,
)


load_dotenv(PROJECT_ROOT / ".env")


class QueueWriter:
    """File-like writer that streams stdout lines into a Queue."""

    def __init__(self, output_queue: queue.Queue):
        self.output_queue = output_queue
        self._buffer = ""

    def write(self, text: str) -> int:
        self._buffer += text
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            if line.strip():
                self.output_queue.put(line.strip())
        return len(text)

    def flush(self) -> None:
        if self._buffer.strip():
            self.output_queue.put(self._buffer.strip())
            self._buffer = ""


def infer_agent_progress(log_line: str) -> str | None:
    checks = [
        (r"research", "🔎 Research Agent coletando inteligência de mercado"),
        (r"copy", "✍️ Copy Agent gerando ativos de conversão"),
        (r"ads", "🎯 Ads Agent transformando copy em scripts/plataformas"),
        (r"director", "🧠 Director Agent validando qualidade final"),
    ]
    lowered = log_line.lower()
    for pattern, message in checks:
        if re.search(pattern, lowered):
            return message
    return None


def run_campaign(goal: str, status_box, progress_placeholder):
    """Execute CrewAI workflow in background and stream progress to UI."""
    output_queue: queue.Queue = queue.Queue()
    result_holder: dict[str, str | Exception | None] = {"result": None, "error": None}

    campaign_id = create_campaign(goal=goal, status="running")

    def worker() -> None:
        writer = QueueWriter(output_queue)
        try:
            output_queue.put("🚀 Inicializando AERYS Crew...")
            system = AerysCrewSystem(campaign_goal=goal)
            output_queue.put("⚙️ Crew inicializada. Executando tarefas sequenciais...")

            from contextlib import redirect_stderr, redirect_stdout

            with redirect_stdout(writer), redirect_stderr(writer):
                result = system.run()

            output_queue.put("💾 Salvando campanha em markdown...")
            output_path = save_output(campaign_goal=goal, content=str(result))
            update_campaign_status(
                campaign_id=campaign_id,
                status="completed",
                file_path=str(output_path),
                date=date.today().isoformat(),
            )
            result_holder["result"] = str(output_path)
            output_queue.put("✅ Campanha concluída com sucesso.")
        except Exception as exc:
            update_campaign_status(campaign_id=campaign_id, status="failed")
            result_holder["error"] = exc
            output_queue.put(f"❌ Erro durante execução: {exc}")

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    last_agent_message = "⏳ Aguardando logs dos agentes..."
    progress_placeholder.info(last_agent_message)

    while thread.is_alive() or not output_queue.empty():
        while not output_queue.empty():
            line = output_queue.get()
            status_box.write(line)
            maybe_agent_update = infer_agent_progress(line)
            if maybe_agent_update:
                last_agent_message = maybe_agent_update
                progress_placeholder.info(last_agent_message)
        time.sleep(0.2)

    if result_holder["error"]:
        status_box.update(label="Execução falhou", state="error", expanded=True)
        raise result_holder["error"]  # type: ignore[misc]

    progress_placeholder.success("✅ Todos os agentes finalizaram a execução.")
    status_box.update(label="Execução finalizada", state="complete", expanded=False)
    return result_holder["result"]


def format_campaign_label(campaign: dict) -> str:
    goal_preview = campaign["goal"][:60] + ("..." if len(campaign["goal"]) > 60 else "")
    run_date = campaign["date"] or campaign["created_at"][:10]
    return f"#{campaign['id']} • {run_date} • {campaign['status']} • {goal_preview}"


def render_sidebar(campaigns: list[dict]) -> None:
    with st.sidebar:
        st.markdown("## ✨ AERYS Command Center")
        st.caption("CrewAI Dashboard • Operação de campanhas")
        st.divider()

        total = len(campaigns)
        completed = len([c for c in campaigns if c["status"] == "completed"])
        success_rate = (completed / total * 100) if total else 0.0

        c1, c2 = st.columns(2)
        c1.metric("Campanhas", total)
        c2.metric("Taxa sucesso", f"{success_rate:.0f}%")

        st.markdown("#### Histórico rápido")
        if campaigns:
            compact_rows = [
                {
                    "ID": c["id"],
                    "Data": c["date"] or c["created_at"][:10],
                    "Status": c["status"],
                }
                for c in campaigns[:20]
            ]
            st.dataframe(compact_rows, use_container_width=True, hide_index=True)

            options = {format_campaign_label(c): c["id"] for c in campaigns}
            selected_label = st.selectbox(
                "Selecionar campanha para visualizar",
                options=list(options.keys()),
                key="sidebar_campaign_selector",
            )
            st.session_state.selected_campaign_id = options[selected_label]
        else:
            st.info("Nenhuma campanha registrada ainda.")


def render_view_campaign_tab(campaigns: list[dict]) -> None:
    st.subheader("Visualizar campanha")

    if not campaigns:
        st.info("Gere uma campanha na aba **New Campaign** para visualizar resultados.")
        return

    campaign_ids = [c["id"] for c in campaigns]
    default_id = st.session_state.get("selected_campaign_id", campaign_ids[0])
    if default_id not in campaign_ids:
        default_id = campaign_ids[0]

    selected_id = st.selectbox(
        "Escolha uma execução",
        options=campaign_ids,
        index=campaign_ids.index(default_id),
        format_func=lambda cid: format_campaign_label(get_campaign_by_id(cid) or campaigns[0]),
        key="main_campaign_selector",
    )

    st.session_state.selected_campaign_id = selected_id
    campaign = get_campaign_by_id(selected_id)
    if not campaign:
        st.error("Não foi possível carregar a campanha selecionada.")
        return

    m1, m2, m3 = st.columns(3)
    m1.metric("Status", campaign["status"])
    m2.metric("Data", campaign["date"] or campaign["created_at"][:10])
    m3.metric("ID", str(campaign["id"]))

    st.markdown("#### Objetivo")
    st.write(campaign["goal"])

    if not campaign.get("file_path"):
        st.warning("Esta campanha ainda não possui arquivo final (ou houve falha na execução).")
        return

    file_path = Path(campaign["file_path"])
    if not file_path.exists():
        st.error(f"Arquivo não encontrado: {file_path}")
        return

    content = file_path.read_text(encoding="utf-8")
    st.markdown("#### Output markdown")
    st.markdown(content)

    st.download_button(
        label="⬇️ Download do arquivo .md",
        data=content,
        file_name=file_path.name,
        mime="text/markdown",
        use_container_width=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="AERYS Command Center",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
            .stApp {
                background: radial-gradient(circle at top left, #101426, #0b0f1a 50%);
            }
            .block-container {
                padding-top: 1.5rem;
                padding-bottom: 2rem;
            }
            h1, h2, h3 {
                letter-spacing: 0.2px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("🚀 AERYS CrewAI Command Center")
    st.caption("Gere, acompanhe e revise campanhas em um único painel operacional.")

    try:
        validate_env()
    except Exception as exc:
        st.error(f"Configuração de ambiente inválida: {exc}")
        st.stop()

    campaigns = get_all_campaigns()
    render_sidebar(campaigns)

    tab_new, tab_view = st.tabs(["New Campaign", "View Campaign"])

    with tab_new:
        st.subheader("Nova campanha")

        flash_success = st.session_state.pop("flash_success", None)
        if flash_success:
            st.success(flash_success)

        campaign_goal = st.text_area(
            "Objetivo da campanha",
            placeholder="Ex.: Create a high-converting TikTok campaign for AERYS jawline angle",
            height=160,
            key="campaign_goal_input",
        )

        generate_clicked = st.button(
            "Generate Campaign",
            type="primary",
            use_container_width=True,
        )

        progress_placeholder = st.empty()

        if generate_clicked:
            if not campaign_goal.strip():
                st.warning("Informe um objetivo de campanha antes de executar.")
            else:
                with st.status("Executando campanha AERYS...", expanded=True) as status_box:
                    try:
                        output_path = run_campaign(
                            goal=campaign_goal.strip(),
                            status_box=status_box,
                            progress_placeholder=progress_placeholder,
                        )
                        st.session_state.last_generated_file = output_path
                        st.session_state.flash_success = (
                            f"Campanha gerada com sucesso em: {output_path}"
                        )
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Falha na execução da campanha: {exc}")

    with tab_view:
        render_view_campaign_tab(get_all_campaigns())


if __name__ == "__main__":
    main()
