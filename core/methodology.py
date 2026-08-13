"""Referenciais metodológicos puros para os diagnósticos do Ranking Siconfi.

As listas de cruzamentos foram transcritas de
``app_dissertacao/src/config/dimensoes_tipo_4.py``, o recorte municipal usado
nas simulações da dissertação. Elas ficam neste módulo para que o aplicativo
não dependa, em tempo de execução, do outro repositório.

Este módulo não executa regras contábeis; apenas registra o escopo anual.
"""

from __future__ import annotations

from math import isnan
from types import MappingProxyType
from typing import Final, Mapping


METHODOLOGY_SOURCE: Final[str] = (
    "Dissertação: src/config/dimensoes_tipo_4.py "
    "(recorte municipal das simulações)"
)


DIMENSOES_CRUZAMENTO_2023: Final[tuple[str, ...]] = (
    "D2_00044", "D2_00046", "D2_00048", "D2_00049", "D2_00050",
    "D2_00058", "D2_00074",

    "D3_00002", "D3_00005", "D3_00006", "D3_00008", "D3_00009",
    "D3_00010", "D3_00014", "D3_00015", "D3_00016", "D3_00017",
    "D3_00022", "D3_00023", "D3_00024", "D3_00025", "D3_00026",
    "D3_00027", "D3_00028",

    "D4_00001", "D4_00002", "D4_00003", "D4_00004", "D4_00005",
    "D4_00006", "D4_00007", "D4_00010", "D4_00012", "D4_00017",
    "D4_00019", "D4_00020", "D4_00022", "D4_00024", "D4_00025",
    "D4_00026", "D4_00029", "D4_00030", "D4_00031", "D4_00032",
    "D4_00033", "D4_00034", "D4_00038", "D4_00040",
)


DIMENSOES_CRUZAMENTO_2024: Final[tuple[str, ...]] = (
    "D2_00044", "D2_00046", "D2_00048", "D2_00049", "D2_00050",
    "D2_00058", "D2_00074",

    "D3_00002", "D3_00005", "D3_00006", "D3_00008", "D3_00009",
    "D3_00010", "D3_00014", "D3_00015", "D3_00016", "D3_00017",
    "D3_00022", "D3_00023", "D3_00024", "D3_00025", "D3_00026",
    "D3_00027", "D3_00028", "D3_00029", "D3_00030", "D3_00032",
    "D3_00033", "D3_00034", "D3_00035", "D3_00037", "D3_00038",
    "D3_00039", "D3_00040", "D3_00044",

    "D4_00001", "D4_00002", "D4_00003", "D4_00004", "D4_00005",
    "D4_00006", "D4_00007", "D4_00010", "D4_00012", "D4_00017",
    "D4_00019", "D4_00020", "D4_00022", "D4_00024", "D4_00025",
    "D4_00026", "D4_00029", "D4_00030", "D4_00031", "D4_00032",
    "D4_00033", "D4_00034", "D4_00038", "D4_00040", "D4_00043",
    "D4_00045",
)


DIMENSOES_CRUZAMENTO_2025: Final[tuple[str, ...]] = (
    "D2_00044", "D2_00046", "D2_00048", "D2_00049", "D2_00050",
    "D2_00058", "D2_00069", "D2_00070", "D2_00071", "D2_00072",
    "D2_00073", "D2_00074", "D2_00100", "D2_00101", "D2_00102",
    "D2_00103", "D2_00104",

    "D3_00002", "D3_00005", "D3_00006", "D3_00008", "D3_00009",
    "D3_00010", "D3_00014", "D3_00015", "D3_00016", "D3_00017",
    "D3_00022", "D3_00023", "D3_00024", "D3_00025", "D3_00026",
    "D3_00027", "D3_00028", "D3_00030", "D3_00032", "D3_00033",
    "D3_00034", "D3_00035", "D3_00037", "D3_00038", "D3_00039",
    "D3_00040", "D3_00044", "D3_00047",

    "D4_00001", "D4_00002", "D4_00003", "D4_00004", "D4_00005",
    "D4_00006", "D4_00007", "D4_00010", "D4_00012", "D4_00017",
    "D4_00019", "D4_00020", "D4_00022", "D4_00024", "D4_00025",
    "D4_00026", "D4_00029", "D4_00030", "D4_00031", "D4_00032",
    "D4_00033", "D4_00034", "D4_00038", "D4_00040", "D4_00043",
    "D4_00046", "D4_00047",
)


# Recorte das verificações de cruzamento que não dependem da MSC. Fonte:
# ``app_publico_dissertacao.py`` da dissertação (linha da constante homônima).
DIMENSOES_CRUZAMENTO_SEM_MSC_2025: Final[tuple[str, ...]] = (
    "D3_00002", "D3_00005", "D3_00006", "D3_00008", "D3_00009",
    "D3_00010", "D3_00014", "D3_00015", "D3_00016", "D3_00017",
    "D3_00027", "D3_00028", "D3_00030", "D3_00032", "D3_00033",
    "D3_00034", "D3_00035", "D3_00037", "D3_00038", "D3_00039",
    "D3_00040", "D3_00044", "D3_00047",

    "D4_00001", "D4_00002", "D4_00003", "D4_00004", "D4_00005",
    "D4_00006", "D4_00007", "D4_00010", "D4_00012", "D4_00017",
    "D4_00019", "D4_00046", "D4_00047",
)


DIMENSOES_CRUZAMENTO_POR_ANO: Final[Mapping[int, tuple[str, ...]]] = (
    MappingProxyType(
        {
            2023: DIMENSOES_CRUZAMENTO_2023,
            2024: DIMENSOES_CRUZAMENTO_2024,
            2025: DIMENSOES_CRUZAMENTO_2025,
        }
    )
)

SUPPORTED_YEARS: Final[tuple[int, ...]] = tuple(DIMENSOES_CRUZAMENTO_POR_ANO)

DIMENSOES_CRUZAMENTO_SEM_MSC_POR_ANO: Final[Mapping[int, tuple[str, ...]]] = (
    MappingProxyType({2025: DIMENSOES_CRUZAMENTO_SEM_MSC_2025})
)


def get_crosschecks(year: int | str, dimension: str | int | None = None) -> tuple[str, ...]:
    """Obtém os cruzamentos autoritativos de um ano, opcionalmente por dimensão.

    Uma tupla é retornada para impedir que uma tela altere acidentalmente o
    referencial compartilhado. Anos fora do recorte da dissertação geram
    ``ValueError`` em vez de reutilizar silenciosamente a metodologia errada.
    """

    try:
        normalized_year = int(year)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Ano metodológico inválido: {year!r}") from exc

    try:
        codes = DIMENSOES_CRUZAMENTO_POR_ANO[normalized_year]
    except KeyError as exc:
        supported = ", ".join(str(item) for item in SUPPORTED_YEARS)
        raise ValueError(
            f"Ano {normalized_year} sem metodologia cadastrada; use {supported}."
        ) from exc

    if dimension is None:
        return codes

    normalized_dimension = str(dimension).strip().upper()
    if normalized_dimension in {"2", "3", "4"}:
        normalized_dimension = f"D{normalized_dimension}"
    if normalized_dimension not in {"D2", "D3", "D4"}:
        raise ValueError(f"Dimensão inválida: {dimension!r}")
    return tuple(code for code in codes if code.startswith(f"{normalized_dimension}_"))


def get_crosscheck_counts(year: int | str) -> dict[str, int]:
    """Retorna as quantidades D2/D3/D4 e o total do ano metodológico."""

    counts = {
        dimension: len(get_crosschecks(year, dimension))
        for dimension in ("D2", "D3", "D4")
    }
    counts["total"] = sum(counts.values())
    return counts


def get_crosschecks_without_msc(
    year: int | str,
    dimension: str | int | None = None,
) -> tuple[str, ...]:
    """Obtém o recorte que pode ser analisado sem dados da MSC.

    A dissertação documenta esse subconjunto apenas para 2025; outro ano gera
    erro explícito para evitar a extrapolação indevida da metodologia.
    """

    try:
        normalized_year = int(year)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Ano metodológico inválido: {year!r}") from exc
    try:
        codes = DIMENSOES_CRUZAMENTO_SEM_MSC_POR_ANO[normalized_year]
    except KeyError as exc:
        raise ValueError(
            f"O recorte sem MSC está documentado somente para 2025, não {normalized_year}."
        ) from exc

    if dimension is None:
        return codes
    normalized_dimension = str(dimension).strip().upper()
    if normalized_dimension in {"3", "4"}:
        normalized_dimension = f"D{normalized_dimension}"
    if normalized_dimension not in {"D3", "D4"}:
        raise ValueError("O recorte sem MSC de 2025 contém somente D3 e D4.")
    return tuple(code for code in codes if code.startswith(f"{normalized_dimension}_"))


# Limites oficiais, expressos em percentual. O limite inferior é inclusivo.
ICF_THRESHOLDS_PERCENT: Final[tuple[tuple[float, str], ...]] = (
    (95.0, "A"),
    (85.0, "B"),
    (75.0, "C"),
    (65.0, "D"),
)
ICF_MISSING_LABEL: Final[str] = "N/A"


def classify_icf(score: object, *, scale: str = "percent") -> str:
    """Classifica o ICF; a escala explícita evita ambiguidade entre 1 e 1%."""
    if score is None:
        return ICF_MISSING_LABEL
    if isinstance(score, bool):
        raise TypeError("O ICF deve ser numérico, não booleano.")
    try:
        percent = float(score)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"ICF não numérico: {score!r}") from exc
    if isnan(percent):
        return ICF_MISSING_LABEL
    if scale == "proportion":
        percent *= 100
    elif scale != "percent":
        raise ValueError("scale deve ser 'percent' ou 'proportion'.")
    if not 0 <= percent <= 100:
        raise ValueError("O ICF deve estar entre 0 e 100.")
    for lower_bound, label in ICF_THRESHOLDS_PERCENT:
        if percent >= lower_bound:
            return label
    return "E"
