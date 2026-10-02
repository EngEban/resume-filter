# ============================================================
# ui/main.py
# Wire NiceGUI into the FastAPI app.
# ============================================================
import logging

from fastapi import FastAPI
from nicegui import app as nicegui_app
from nicegui import ui

from app.core.config import settings
from ui.pages import (
    b2b_batch_analytics,
    b2b_batch_detail,
    b2b_batches,
    b2b_compare,
    b2b_resume_detail,
    b2b_settings,
    b2c_analyze,
    b2c_history,
    dashboard,
    landing,
    login,
    register,
)
from ui.theme import apply_global_css

logger = logging.getLogger(__name__)


def register_ui(fastapi_app: FastAPI) -> None:
    """
    Mount the NiceGUI frontend under /ui on the FastAPI app.

    Page paths here are relative to /ui. So @ui.page("/login")
    becomes /ui/login.
    """
    @nicegui_app.on_startup
    async def _setup_global_css() -> None:
        apply_global_css()

    # ---------- Public ----------
    @ui.page("/")
    def _landing() -> None:
        landing.render()

    @ui.page("/login")
    def _login() -> None:
        login.render()

    @ui.page("/register")
    def _register() -> None:
        register.render()

    # ---------- Authenticated ----------
    @ui.page("/dashboard")
    def _dashboard() -> None:
        dashboard.render()

    @ui.page("/b2c/analyze")
    def _b2c_analyze() -> None:
        b2c_analyze.render()

    @ui.page("/b2c/history")
    def _b2c_history() -> None:
        b2c_history.render()

    @ui.page("/b2b/batches")
    def _b2b_batches() -> None:
        b2b_batches.render()

    @ui.page("/b2b/batches/{batch_id}")
    def _b2b_batch_detail(batch_id: str) -> None:
        b2b_batch_detail.render(batch_id)

    @ui.page("/b2b/batches/{batch_id}/analytics")
    def _b2b_batch_analytics(batch_id: str) -> None:
        b2b_batch_analytics.render(batch_id)

    @ui.page("/b2b/batches/{batch_id}/compare")
    def _b2b_compare(batch_id: str) -> None:
        b2b_compare.render(batch_id)

    @ui.page("/b2b/resumes/{resume_id}")
    def _b2b_resume_detail(resume_id: str) -> None:
        b2b_resume_detail.render(resume_id)

    @ui.page("/b2b/settings")
    def _b2b_settings() -> None:
        b2b_settings.render()

    # ---------- Mount ----------
    ui.run_with(
        fastapi_app,
        mount_path="/ui",
        storage_secret=settings.UI_STORAGE_SECRET,
        title="ResumeFilter",
        favicon="📄",
    )

    logger.info("NiceGUI mounted at /ui")