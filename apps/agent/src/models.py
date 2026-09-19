"""Pydantic models + LangGraph state schema for MSB SmartForm AI."""
from __future__ import annotations

from typing import Annotated, Optional

from pydantic import BaseModel, Field


# --- Form metadata (matches Form Registry 12 columns) ---
class FormMeta(BaseModel):
    code: str
    name: str
    name_en: Optional[str] = None
    business_group: str
    segment: str  # KHCN | KHTC | KHCN/KHTC | FDI
    org_type: str
    use_case: str
    preparer: str
    signer: str
    accompanying_docs: list[str] = Field(default_factory=list)
    version: str
    effective_date: str
    source_file: str
    active: bool = True
    bilingual: bool = False


class FormField(BaseModel):
    key: str
    label: str
    label_en: Optional[str] = None
    type: str  # text | enum | number | date | bool
    required: bool = False
    validation: Optional[str] = None
    options: list[str] = Field(default_factory=list)
    note: Optional[str] = None


class Signatory(BaseModel):
    who: str
    position: str
    position_to_sign: str
    stamp: str  # Có | Không | Theo mẫu (optional)


class FormTemplate(BaseModel):
    meta: FormMeta
    fields: list[FormField] = Field(default_factory=list)
    signatories: list[Signatory] = Field(default_factory=list)
    fixed_content: list[str] = Field(default_factory=list)
    reject_list: list[str] = Field(default_factory=list)
    branches: list[str] = Field(default_factory=list)


# --- Customer (demo) ---
class Customer(BaseModel):
    name: str
    name_en: Optional[str] = None
    type: str  # org | individual
    org_type: Optional[str] = None  # CP | TNHH1TV | TNHH2TV | DNTN | FDI
    is_fdi: bool = False
    tax_id: Optional[str] = None
    account_no: Optional[str] = None
    legal_rep: Optional[str] = None
    legal_rep_nationality: Optional[str] = None
    legal_rep_passport: Optional[str] = None
    cccd: Optional[str] = None
    is_demo: bool = True


# --- QC ---
class CheckResult(BaseModel):
    name: str
    pass_: bool = True
    detail: Optional[str] = None


class QCResult(BaseModel):
    status: str  # READY | MISSING INFORMATION | NEED MSB REVIEW
    checks: list[CheckResult] = Field(default_factory=list)


# --- LangGraph state ---
class AgentState(BaseModel):
    session_id: str = ""
    step: int = 1
    customer: Optional[Customer] = None
    intents: list[str] = Field(default_factory=list)
    selected_forms: list[FormMeta] = Field(default_factory=list)
    collected: dict[str, str] = Field(default_factory=dict)
    missing: list[str] = Field(default_factory=list)
    filled: dict[str, str] = Field(default_factory=dict)
    qc: Optional[QCResult] = None
    signatories: list[Signatory] = Field(default_factory=list)
    checklist: list[dict] = Field(default_factory=list)
    messages: list[dict] = Field(default_factory=list)
    last_question: Optional[str] = None
    output: Optional[dict] = None
    not_found: bool = False
    soan_ho_so: bool = False
