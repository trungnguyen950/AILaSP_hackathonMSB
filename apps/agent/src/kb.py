"""Knowledge Base loader: parse form-registry.md + form template MD files."""
from __future__ import annotations

import os
import re
from pathlib import Path

from .models import FormField, FormMeta, FormTemplate, Signatory

KB_DIR = Path(os.environ.get("KB_DIR", Path(__file__).resolve().parent.parent / "knowledge_base"))


def _split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _parse_table(lines: list[str], start: int) -> tuple[list[list[str]], int]:
    """Parse a markdown table starting near `start`. Returns (rows, next_index)."""
    rows: list[list[str]] = []
    i = start
    while i < len(lines) and not lines[i].strip().startswith("|"):
        i += 1
    # header
    if i >= len(lines):
        return rows, i
    header = _split_row(lines[i])
    i += 1
    # separator
    if i < len(lines) and re.match(r"^\|[\s\-:|]+\|?\s*$", lines[i]):
        i += 1
    # data rows
    while i < len(lines) and lines[i].strip().startswith("|"):
        rows.append(_split_row(lines[i]))
        i += 1
    return rows, i


def load_registry() -> list[FormMeta]:
    """Parse form-registry.md into a list of FormMeta."""
    path = KB_DIR / "form-registry.md"
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    rows, _ = _parse_table(lines, 0)
    metas: list[FormMeta] = []
    for r in rows:
        if len(r) < 12 or not r[0].startswith("MSB"):
            continue
        accom = [d.strip() for d in re.split(r"[;·,]", r[8]) if d.strip()]
        metas.append(
            FormMeta(
                code=r[0],
                name=r[1],
                business_group=r[2],
                segment=r[3],
                org_type=r[4],
                use_case=r[5],
                preparer=r[6],
                signer=r[7],
                accompanying_docs=accom,
                version=r[9],
                effective_date=r[10],
                source_file=r[11],
                active=True,
                bilingual="FDI" in r[3] or "FDI" in r[4] or "song" in r[1].lower() or "bilingual" in r[5].lower(),
            )
        )
    return metas


def _find_section(lines: list[str], heading: str) -> int:
    for i, ln in enumerate(lines):
        if ln.strip().startswith("#") and heading.lower() in ln.lower():
            return i
    return -1


def load_template(meta: FormMeta) -> FormTemplate:
    """Parse a single form template MD file into FormTemplate."""
    path = KB_DIR / "forms" / f"{meta.code}.md"
    fields: list[FormField] = []
    signatories: list[Signatory] = []
    fixed_content: list[str] = []
    reject_list: list[str] = []
    branches: list[str] = []

    if not path.exists():
        return FormTemplate(meta=meta)

    lines = path.read_text(encoding="utf-8").splitlines()

    # fields
    idx = _find_section(lines, "Trường biểu mẫu")
    if idx >= 0:
        rows, _ = _parse_table(lines, idx + 1)
        for r in rows:
            if len(r) < 6 or r[1] == "key":
                continue
            try:
                required = r[4].strip().lower() in ("yes", "true", "có")
            except IndexError:
                required = False
            validation = r[5].strip() if len(r) > 5 else None
            note = r[6].strip() if len(r) > 6 else None
            label_en = r[7].strip() if len(r) > 7 and r[7].strip() else None
            options: list[str] = []
            if validation and "/" in validation and "OR" not in validation:
                options = [o.strip() for o in validation.split("/") if o.strip()]
            fields.append(
                FormField(key=r[1], label=r[2], label_en=label_en, type=r[3], required=required, validation=validation, note=note, options=options)
            )

    # signatories
    idx = _find_section(lines, "Người ký")
    if idx >= 0:
        rows, _ = _parse_table(lines, idx + 1)
        for r in rows:
            if len(r) < 4 or r[0] == "Người ký":
                continue
            signatories.append(Signatory(who=r[0], position=r[1], position_to_sign=r[2], stamp=r[3]))

    # fixed content
    idx = _find_section(lines, "Nội dung cố định")
    if idx >= 0:
        for ln in lines[idx + 1 :]:
            if ln.strip().startswith("#"):
                break
            if ln.strip().startswith("- "):
                fixed_content.append(ln.strip()[2:])

    # reject list
    idx = _find_section(lines, "Reject list")
    if idx >= 0:
        for ln in lines[idx + 1 :]:
            if ln.strip().startswith("#"):
                break
            clean = re.sub(r"[*_>]", "", ln).strip()
            if clean:
                reject_list.extend([c.strip() for c in re.split(r"[,·]", clean) if c.strip()])

    # branches
    idx = _find_section(lines, "Phân nhánh")
    if idx >= 0:
        for ln in lines[idx + 1 :]:
            if ln.strip().startswith("#"):
                break
            if "·" in ln:
                branches = [b.strip() for b in ln.split("·") if b.strip()]

    return FormTemplate(
        meta=meta,
        fields=fields,
        signatories=signatories,
        fixed_content=fixed_content,
        reject_list=reject_list,
        branches=branches,
    )


class KnowledgeBase:
    def __init__(self) -> None:
        self.metas = load_registry()
        self.templates: dict[str, FormTemplate] = {}
        for m in self.metas:
            self.templates[m.code] = load_template(m)

    def get(self, code: str) -> FormTemplate | None:
        return self.templates.get(code)

    def list_active(self) -> list[FormMeta]:
        return [m for m in self.metas if m.active]


# Eager singleton (built once at import)
KB = KnowledgeBase()
