# ============================================================
# ui/api_client.py
# HTTP client for the UI to talk to the FastAPI backend.
# ============================================================
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "http://127.0.0.1:8000/api/v1"
DEFAULT_TIMEOUT = 120.0


class APIError(Exception):
    """Raised when the backend returns an error."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"[{status_code}] {message}")


class APIClient:
    """Thin httpx wrapper for backend calls."""

    def __init__(self, base_url: str = DEFAULT_BASE_URL) -> None:
        self.base_url = base_url.rstrip("/")
        self.token: str | None = None

    # ---------- internals ----------
    def _headers(self, extra: dict | None = None) -> dict:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if extra:
            headers.update(extra)
        return headers

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict | None = None,
        data: dict | None = None,
        files: list | None = None,
        extra_headers: dict | None = None,
        params: dict | None = None,
    ) -> Any:
        url = f"{self.base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                response = await client.request(
                    method,
                    url,
                    json=json,
                    data=data,
                    files=files,
                    headers=self._headers(extra_headers),
                    params=params,
                )
        except httpx.RequestError as exc:
            logger.error("Backend request failed: %s", exc)
            raise APIError(0, "Network error. Please try again.") from exc

        if response.status_code >= 400:
            try:
                body = response.json()
                message = body.get("message") or body.get("detail") or "Error"
            except Exception:
                message = response.text or "Error"
            raise APIError(response.status_code, message)

        if response.status_code == 204:
            return None
        try:
            return response.json()
        except Exception:
            return response.text

    async def _download(self, path: str, params: dict | None = None) -> bytes:
        """Download binary content (Excel/PDF)."""
        url = f"{self.base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                response = await client.get(
                    url, headers=self._headers(), params=params
                )
        except httpx.RequestError as exc:
            logger.error("Download failed: %s", exc)
            raise APIError(0, "Network error. Please try again.") from exc

        if response.status_code >= 400:
            try:
                body = response.json()
                message = body.get("message") or body.get("detail") or "Error"
            except Exception:
                message = response.text or "Download failed"
            raise APIError(response.status_code, message)
        return response.content

    # ---------- auth ----------
    async def login(self, email: str, password: str) -> dict:
        return await self._request(
            "POST",
            "/auth/login",
            data={"username": email, "password": password},
            extra_headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    async def register_b2c(self, email: str, password: str) -> dict:
        return await self._request(
            "POST",
            "/auth/register/b2c",
            json={
                "email": email,
                "password": password,
                "account_type": "b2c",
            },
        )

    async def register_b2b(
        self,
        organization_name: str,
        organization_slug: str,
        email: str,
        password: str,
    ) -> dict:
        return await self._request(
            "POST",
            "/auth/register/b2b",
            json={
                "organization_name": organization_name,
                "organization_slug": organization_slug,
                "email": email,
                "password": password,
            },
        )

    async def me(self) -> dict:
        return await self._request("GET", "/auth/me")

    # ---------- b2c ----------
    async def analyze(self, resume_text: str, job_description: str) -> dict:
        return await self._request(
            "POST",
            "/b2c/analyze",
            json={
                "resume_text": resume_text,
                "job_description": job_description,
            },
        )

    async def b2c_history(self, limit: int = 20) -> list:
        return await self._request("GET", f"/b2c/history?limit={limit}")

    # ---------- b2b batches ----------
    async def list_batches(
        self,
        status: str | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list:
        params: dict = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        if search:
            params["search"] = search
        return await self._request("GET", "/b2b/batches", params=params)

    async def create_batch(
        self,
        job_title: str,
        job_description: str,
        files: list,
        job_requirements: str | None = None,
    ) -> dict:
        data: dict = {
            "job_title": job_title,
            "job_description": job_description,
        }
        if job_requirements:
            data["job_requirements"] = job_requirements
        return await self._request(
            "POST",
            "/b2b/batches",
            data=data,
            files=files,
        )

    async def get_batch(self, batch_id: str) -> dict:
        return await self._request("GET", f"/b2b/batches/{batch_id}")

    async def list_batch_resumes(
        self,
        batch_id: str,
        search: str | None = None,
        status_filter: str | None = None,
        min_score: float | None = None,
        sort: str = "score_desc",
    ) -> list:
        params: dict = {"sort": sort}
        if search:
            params["search"] = search
        if status_filter:
            params["status"] = status_filter
        if min_score is not None:
            params["min_score"] = min_score
        return await self._request(
            "GET",
            f"/b2b/batches/{batch_id}/resumes",
            params=params,
        )

    async def reprocess_batch(self, batch_id: str) -> dict:
        return await self._request(
            "POST", f"/b2b/batches/{batch_id}/reprocess"
        )

    async def export_batch_xlsx(self, batch_id: str) -> bytes:
        return await self._download(f"/b2b/batches/{batch_id}/export.xlsx")

    async def export_batch_pdf(self, batch_id: str) -> bytes:
        return await self._download(f"/b2b/batches/{batch_id}/export.pdf")

    # ---------- b2b results ----------
    async def get_resume_report(self, resume_id: str) -> dict:
        return await self._request("GET", f"/b2b/resumes/{resume_id}")

    async def export_resume_pdf(self, resume_id: str) -> bytes:
        return await self._download(f"/b2b/resumes/{resume_id}/report.pdf")

    async def compare_candidates(self, batch_id: str, limit: int = 5) -> dict:
        return await self._request(
            "GET",
            "/b2b/resumes/compare",
            params={"batch_id": batch_id, "limit": limit},
        )

    async def export_comparison_xlsx(
        self, batch_id: str, limit: int = 10
    ) -> bytes:
        return await self._download(
            "/b2b/resumes/compare/export.xlsx",
            params={"batch_id": batch_id, "limit": limit},
        )

    # ---------- b2b analytics ----------
    async def batch_analytics(self, batch_id: str) -> dict:
        return await self._request(
            "GET", f"/b2b/analytics/batches/{batch_id}"
        )

    async def tenant_overview(self) -> dict:
        return await self._request("GET", "/b2b/analytics/overview")

    # ---------- b2b settings ----------
    async def get_llm_settings(self) -> dict:
        return await self._request("GET", "/b2b/settings/llm")

    async def update_llm_settings(
        self,
        provider: str,
        model: str,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> dict:
        payload: dict = {"provider": provider, "model": model}
        if api_key:
            payload["api_key"] = api_key
        if base_url:
            payload["base_url"] = base_url
        return await self._request("PUT", "/b2b/settings/llm", json=payload)

    async def delete_llm_settings(self) -> None:
        await self._request("DELETE", "/b2b/settings/llm")

    async def list_providers(self) -> dict:
        return await self._request("GET", "/b2b/settings/llm/providers")

    async def test_llm_connection(
        self,
        provider: str,
        model: str,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> dict:
        payload: dict = {"provider": provider, "model": model}
        if api_key:
            payload["api_key"] = api_key
        if base_url:
            payload["base_url"] = base_url
        return await self._request(
            "POST", "/b2b/settings/llm/test", json=payload
        )