"""Tests des exporteurs (txt, pdf, docx)."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from triskell_sales_tunnel.exporters import (
    ExportPayload,
    export_docx,
    export_pdf,
    export_txt,
)


@pytest.fixture
def payload() -> ExportPayload:
    return ExportPayload(
        body=(
            "Bonjour Jordan,\n\n"
            "Voici un message de prospection.\n"
            "Ligne avec accents : éàùç€.\n\n"
            "Cordialement,\nTriskell Studio"
        ),
        subject="Sujet de test — accents éàù",
        product_label="Triskell Studio — Sites web",
        client_label="TPE / PME bretonnes",
        channel_label="Email",
    )


def test_export_txt_writes_file(payload: ExportPayload, tmp_path: Path) -> None:
    dest = tmp_path / "out.txt"
    result = export_txt(payload, dest)
    assert result == dest
    content = dest.read_text(encoding="utf-8")
    assert "Triskell Sales Tunnel" in content
    assert "Bonjour Jordan" in content
    assert "éàùç€" in content
    assert "Sujet de test" in content


def test_export_txt_no_subject(tmp_path: Path) -> None:
    payload = ExportPayload(
        body="Message court.",
        subject="",
        product_label="X",
        client_label="Y",
        channel_label="LinkedIn",
    )
    dest = tmp_path / "out.txt"
    export_txt(payload, dest)
    content = dest.read_text(encoding="utf-8")
    assert "Objet" not in content
    assert "Message court." in content


def test_export_pdf_creates_valid_pdf(payload: ExportPayload, tmp_path: Path) -> None:
    dest = tmp_path / "out.pdf"
    export_pdf(payload, dest)
    assert dest.exists()
    head = dest.read_bytes()[:5]
    assert head == b"%PDF-", "Le fichier doit commencer par le magic %PDF-"
    assert dest.stat().st_size > 1000


def test_export_pdf_handles_long_body(tmp_path: Path) -> None:
    long_body = "\n".join([f"Ligne {i} qui peut être longue " * 4 for i in range(80)])
    payload = ExportPayload(
        body=long_body,
        subject="Long",
        product_label="Test",
        client_label="Test",
        channel_label="Email",
    )
    dest = tmp_path / "long.pdf"
    export_pdf(payload, dest)
    assert dest.exists()
    assert dest.read_bytes().startswith(b"%PDF-")


def test_export_docx_creates_valid_docx(payload: ExportPayload, tmp_path: Path) -> None:
    dest = tmp_path / "out.docx"
    export_docx(payload, dest)
    assert dest.exists()
    # Un .docx est un ZIP avec un fichier word/document.xml
    with zipfile.ZipFile(dest) as zf:
        names = zf.namelist()
        assert "word/document.xml" in names
        body_xml = zf.read("word/document.xml").decode("utf-8")
        assert "Bonjour Jordan" in body_xml
        # Les accents sont préservés
        assert "éàù" in body_xml or "&#" in body_xml  # encodage XML possible
