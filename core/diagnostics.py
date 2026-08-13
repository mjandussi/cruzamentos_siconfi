"""Resumo simples dos DataFrames retornados pelas regras existentes."""

from __future__ import annotations

from enum import Enum
import unicodedata


class DiagnosticStatus(str, Enum):
    CONFORME = "conforme"
    DIVERGENCIA = "divergência"
    DADOS_INSUFICIENTES = "dados insuficientes"
    NAO_APLICAVEL = "não aplicável"
    FALHA_TECNICA = "falha técnica"


def _text(value: object) -> str:
    value = "" if value is None else str(value)
    value = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in value if not unicodedata.combining(char))


def classify_result(response: object, observation: object = "") -> DiagnosticStatus:
    """Classifica apenas o vocabulário que as regras atuais já retornam."""
    answer = _text(response).strip()
    note = _text(observation)
    context = f"{answer} {note}"

    if any(marker in context for marker in (
        "erro ao", "exception", "traceback", "timeout", "api indisponivel",
    )):
        return DiagnosticStatus.FALHA_TECNICA
    if any(marker in context for marker in (
        "nao disponivel", "indisponivel", "nao enviad", "sem dados",
        "dados insuficientes", "analise removida", "nao implementad",
    )):
        return DiagnosticStatus.DADOS_INSUFICIENTES
    if answer.startswith("ok") or " ok" in answer:
        return DiagnosticStatus.CONFORME
    if "erro" in answer or "divergencia" in answer:
        return DiagnosticStatus.DIVERGENCIA
    if (
        answer in {"n/a", "na", "nao aplicavel", "nao se aplica"}
        or "nao se aplica" in note
        or "nao aplicavel" in note
    ):
        return DiagnosticStatus.NAO_APLICAVEL
    return DiagnosticStatus.FALHA_TECNICA


def summarize_results(records: list[dict], expected_codes: tuple[str, ...]) -> dict:
    """Conta cobertura/conformidade, globalmente e por D2/D3/D4."""
    by_code = {
        str(row.get("Dimensão", "")): classify_result(
            row.get("Resposta"), row.get("OBS")
        )
        for row in records
        if str(row.get("Dimensão", "")) in expected_codes
    }

    def bucket(codes: tuple[str, ...]) -> dict:
        statuses = [by_code[code] for code in codes if code in by_code]
        counts = {status.value: statuses.count(status) for status in DiagnosticStatus}
        conclusive = counts[DiagnosticStatus.CONFORME.value] + counts[DiagnosticStatus.DIVERGENCIA.value]
        expected = len(codes)
        return {
            "expected": expected,
            "received": len(statuses),
            "conclusive": conclusive,
            "missing": expected - len(statuses),
            "coverage_percent": (100 * conclusive / expected) if expected else 0.0,
            "conformity_percent": (
                100 * counts[DiagnosticStatus.CONFORME.value] / conclusive
                if conclusive else 0.0
            ),
            "status_counts": counts,
        }

    return {
        "overall": bucket(expected_codes),
        "by_dimension": {
            dimension: bucket(tuple(code for code in expected_codes if code.startswith(dimension)))
            for dimension in ("D2", "D3", "D4")
        },
        "status_by_code": by_code,
    }
