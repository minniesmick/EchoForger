# core/archive_manager.py
"""
EchoForge — Transkript Arşivi.

SQLite veritabanında transkriptleri saklar.
nomic-embed-text (Ollama) ile semantic arama yapar.

Tablo şeması:
    transcripts(
        id          INTEGER PRIMARY KEY,
        filename    TEXT,
        filepath    TEXT,
        text        TEXT,
        language    TEXT,
        duration    REAL,
        segments    TEXT,       ← JSON
        embedding   BLOB,       ← numpy float32 array
        created_at  TEXT
    )
"""
from __future__ import annotations

import json
import sqlite3
import struct
from datetime import datetime
from pathlib import Path
from typing import Any

from core.environment import Environment

# DB dosyası proje kökünde
_DB_PATH = Environment.instance().project_root() / "echoforge_archive.db"


# ══════════════════════════════════════════════════════════════════════════════
#  Veritabanı yönetimi
# ══════════════════════════════════════════════════════════════════════════════

def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Tabloyu oluşturur (zaten varsa dokunmaz)."""
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transcripts (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                filename   TEXT    NOT NULL,
                filepath   TEXT,
                text       TEXT    NOT NULL,
                language   TEXT    DEFAULT '',
                duration   REAL    DEFAULT 0.0,
                segments   TEXT    DEFAULT '[]',
                embedding  BLOB,
                created_at TEXT    NOT NULL
            )
        """)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_created ON transcripts(created_at)"
        )
        conn.commit()


# ══════════════════════════════════════════════════════════════════════════════
#  Embedding
# ══════════════════════════════════════════════════════════════════════════════

def _embed(text: str) -> list[float] | None:
    """nomic-embed-text ile Ollama'dan embedding alır."""
    try:
        import urllib.request
        from core.settings_manager import SettingsManager
        base = SettingsManager.instance().get("ollama_url", "http://localhost:11434")

        body = json.dumps({
            "model": "nomic-embed-text",
            "prompt": text[:2000],   # çok uzun metni kırp
        }).encode()

        req = urllib.request.Request(
            f"{base}/api/embeddings",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data.get("embedding")
    except Exception:
        return None


def _vec_to_blob(vec: list[float]) -> bytes:
    return struct.pack(f"{len(vec)}f", *vec)


def _blob_to_vec(blob: bytes) -> list[float]:
    n = len(blob) // 4
    return list(struct.unpack(f"{n}f", blob))


def _cosine_sim(a: list[float], b: list[float]) -> float:
    dot  = sum(x * y for x, y in zip(a, b))
    na   = sum(x * x for x in a) ** 0.5
    nb   = sum(x * x for x in b) ** 0.5
    return dot / (na * nb + 1e-9)


# ══════════════════════════════════════════════════════════════════════════════
#  CRUD
# ══════════════════════════════════════════════════════════════════════════════

def save_transcript(
    filename:  str,
    text:      str,
    filepath:  str  = "",
    language:  str  = "",
    duration:  float = 0.0,
    segments:  list  = None,
) -> int:
    """
    Transkripti kaydeder, embedding oluşturur.
    Döndürür: yeni kayıt id'si
    """
    init_db()

    seg_json  = json.dumps(segments or [], ensure_ascii=False)
    embedding = _embed(text)
    emb_blob  = _vec_to_blob(embedding) if embedding else None

    with _get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO transcripts
                (filename, filepath, text, language, duration, segments, embedding, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                filename, filepath, text, language,
                duration, seg_json, emb_blob,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        conn.commit()
        return cur.lastrowid


def get_all(limit: int = 200) -> list[dict]:
    """En yeni kayıtları döndürür."""
    init_db()
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT id, filename, language, duration, created_at, text "
            "FROM transcripts ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_by_id(record_id: int) -> dict | None:
    init_db()
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM transcripts WHERE id = ?", (record_id,)
        ).fetchone()
    return dict(row) if row else None


def delete_by_id(record_id: int) -> None:
    init_db()
    with _get_conn() as conn:
        conn.execute("DELETE FROM transcripts WHERE id = ?", (record_id,))
        conn.commit()


def keyword_search(query: str, limit: int = 50) -> list[dict]:
    """SQLite FTS benzeri LIKE araması."""
    init_db()
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT id, filename, language, duration, created_at, text "
            "FROM transcripts WHERE text LIKE ? "
            "ORDER BY created_at DESC LIMIT ?",
            (f"%{query}%", limit),
        ).fetchall()
    return [dict(r) for r in rows]


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    nomic-embed-text ile semantic (vektör) arama.
    Embedding yoksa keyword_search'e düşer.
    """
    init_db()

    q_vec = _embed(query)
    if not q_vec:
        return keyword_search(query, top_k)

    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT id, filename, language, duration, created_at, text, embedding "
            "FROM transcripts WHERE embedding IS NOT NULL"
        ).fetchall()

    scored: list[tuple[float, dict]] = []
    for row in rows:
        r = dict(row)
        vec  = _blob_to_vec(r.pop("embedding"))
        sim  = _cosine_sim(q_vec, vec)
        scored.append((sim, r))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored[:top_k]]


def stats() -> dict:
    """Arşiv istatistikleri."""
    init_db()
    with _get_conn() as conn:
        total    = conn.execute("SELECT COUNT(*) FROM transcripts").fetchone()[0]
        has_emb  = conn.execute(
            "SELECT COUNT(*) FROM transcripts WHERE embedding IS NOT NULL"
        ).fetchone()[0]
        dur_sum  = conn.execute(
            "SELECT SUM(duration) FROM transcripts"
        ).fetchone()[0] or 0.0
    return {
        "total":          total,
        "with_embedding": has_emb,
        "total_duration": dur_sum,
    }
