#!/usr/bin/env python3
"""Build clean submission exports from manuscript/manuscript.md."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "manuscript" / "manuscript.md"
PACKAGE = ROOT / "submission_package"


def run(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def prevent_table_row_splits(path: Path) -> None:
    """Keep each table row together when Word or LibreOffice paginates."""
    document = Document(path)
    for table in document.tables:
        for row in table.rows:
            tr_pr = row._tr.get_or_add_trPr()
            if tr_pr.find(qn("w:cantSplit")) is None:
                tr_pr.append(OxmlElement("w:cantSplit"))
    document.save(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("all", "docx", "pdf", "tex"), default="all")
    args = parser.parse_args()
    PACKAGE.mkdir(exist_ok=True)
    shutil.copy2(SOURCE, PACKAGE / "MANUSCRIPT.md")

    stale_names = (
        "RESPONSE_TO_REVIEWERS.md",
        "AUTHOR_DETAILS_AND_DECLARATIONS.md",
        "RESEARCH_HIGHLIGHTS.md",
    )
    for name in stale_names:
        old = PACKAGE / name
        if old.exists():
            old.unlink()

    figures_src = ROOT / "figures"
    figures_dst = PACKAGE / "figures"
    if figures_dst.exists():
        shutil.rmtree(figures_dst)
    figures_dst.mkdir(parents=True, exist_ok=True)

    # Copy strictly the figures referenced in canonical manuscript
    import re
    manuscript_text = SOURCE.read_text(encoding="utf-8")
    fig_matches = re.findall(r'!\[.*?\]\((?:figures/)?([^)]+)\)', manuscript_text)
    for fig_name in fig_matches:
        src_path = figures_src / fig_name
        if src_path.exists():
            shutil.copy2(src_path, figures_dst / fig_name)

    bibliography = ROOT / "references" / "references.bib"
    shutil.copy2(bibliography, PACKAGE / "REFERENCES.bib")

    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise SystemExit("Pandoc was not found on PATH")
    docx = PACKAGE / "MANUSCRIPT.docx"
    tex = PACKAGE / "MANUSCRIPT.tex"
    resource_path = f".:{ROOT}:{ROOT}/figures:{PACKAGE}:{PACKAGE}/figures"
    if args.format in ("all", "docx", "pdf"):
        run([pandoc, str(SOURCE), "--from=markdown+tex_math_single_backslash", f"--resource-path={resource_path}", "--to=docx", "--standalone", "-o", str(docx)])
        prevent_table_row_splits(docx)
    if args.format in ("all", "tex"):
        run([pandoc, str(SOURCE), "--from=markdown+tex_math_single_backslash", f"--resource-path={resource_path}", "--to=latex", "--standalone", "-o", str(tex)])
    if args.format in ("all", "pdf"):
        soffice = shutil.which("soffice") or shutil.which("libreoffice")
        chrome = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        if soffice:
            run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(PACKAGE), str(docx)])
        elif chrome.exists():
            html_temp = PACKAGE / "MANUSCRIPT_temp.html"
            run([
                pandoc,
                str(SOURCE),
                "--from=markdown+tex_math_single_backslash",
                f"--resource-path={resource_path}",
                "--to=html5",
                "--standalone",
                "--embed-resources",
                "-o",
                str(html_temp),
            ])
            run([
                str(chrome),
                "--headless",
                "--disable-gpu",
                f"--print-to-pdf={PACKAGE / 'MANUSCRIPT.pdf'}",
                str(html_temp),
            ])
            if html_temp.exists():
                html_temp.unlink()
        else:
            if args.format == "pdf":
                raise SystemExit("Neither LibreOffice (soffice) nor Google Chrome was found to render PDF.")
            print("Notice: Neither LibreOffice nor Google Chrome was found; skipping PDF update.")

    # Rebuild clean submission_package.zip
    zip_path = ROOT / "submission_package.zip"
    if zip_path.exists():
        zip_path.unlink()
    run(["zip", "-r", "submission_package.zip", "submission_package"])

    # Recompute submission_package.sha256
    import hashlib
    manifest_lines = []
    files_to_hash = [
        "submission_package/COVER_LETTER.md",
        "submission_package/HIGHLIGHTS.md",
        "submission_package/MANUSCRIPT.docx",
        "submission_package/MANUSCRIPT.md",
        "submission_package/MANUSCRIPT.pdf",
        "submission_package/MANUSCRIPT.tex",
        "submission_package/README.md",
        "submission_package/REFERENCES.bib",
        "submission_package/figures/fig1_pipeline_timing.png",
        "submission_package/figures/fig2_offered_load.png",
        "submission_package/figures/fig3_paired_comparison.png",
        "submission_package.zip",
    ]
    for rel_path in files_to_hash:
        p = ROOT / rel_path
        if p.exists():
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            manifest_lines.append(f"{h}  {rel_path}\n")
    (ROOT / "submission_package.sha256").write_text("".join(manifest_lines))
    print("+ Updated submission_package.sha256")


if __name__ == "__main__":
    main()
