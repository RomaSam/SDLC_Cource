"""Thin HTTP client that wraps the Cinema REST API."""

import httpx
from config import settings


def _headers() -> dict[str, str]:
    return {"X-API-Key": settings.api_key}


def _url(path: str) -> str:
    return f"{settings.api_base_url.rstrip('/')}{path}"


# ── screenings ──────────────────────────────────────────────────────────────

def list_screenings(
    genre: str | None = None,
    date: str | None = None,
    hall: str | None = None,
) -> list[dict]:
    params = {k: v for k, v in {"genre": genre, "date": date, "hall": hall}.items() if v is not None}
    r = httpx.get(_url("/screenings/"), headers=_headers(), params=params)
    r.raise_for_status()
    return r.json()


def get_screening(screening_id: int) -> dict:
    r = httpx.get(_url(f"/screenings/{screening_id}"), headers=_headers())
    r.raise_for_status()
    return r.json()


def create_screening(data: dict) -> dict:
    r = httpx.post(_url("/screenings/"), headers=_headers(), json=data)
    r.raise_for_status()
    return r.json()


def replace_screening(screening_id: int, data: dict) -> dict:
    r = httpx.put(_url(f"/screenings/{screening_id}"), headers=_headers(), json=data)
    r.raise_for_status()
    return r.json()


def patch_screening(screening_id: int, data: dict) -> dict:
    r = httpx.patch(_url(f"/screenings/{screening_id}"), headers=_headers(), json=data)
    r.raise_for_status()
    return r.json()


def delete_screening(screening_id: int) -> None:
    r = httpx.delete(_url(f"/screenings/{screening_id}"), headers=_headers())
    r.raise_for_status()
