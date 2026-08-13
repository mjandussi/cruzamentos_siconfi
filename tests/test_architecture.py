"""Proteções simples contra a reintrodução dos módulos legados removidos."""

from __future__ import annotations

import ast
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LEGACY_MODULES = {
    "artefato_completo",
    "core.entes",
    "api_ranking.analysis.d1",
    "api_ranking.analysis.d2_antecipada",
    "api_ranking.renders.render_d1",
    "api_ranking.renders.render_d2",
    "api_ranking.renders.render_d2_antecipada",
    "api_ranking.renders.render_d3",
    "api_ranking.renders.render_d4",
    "api_ranking.services.check_types",
    "api_ranking.services.formatting",
    "core.utils",
    "render_d2",
    "render_d3",
    "render_d4",
}


class ArchitectureTests(unittest.TestCase):
    def test_entrypoints_do_not_import_removed_legacy_modules(self):
        entrypoints = [
            PROJECT_ROOT / "app.py",
            *sorted((PROJECT_ROOT / "pages").glob("*.py")),
        ]
        offenders: list[str] = []

        for path in entrypoints:
            tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
            imported: set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.update(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    imported.add(node.module)

            for module in sorted(imported & LEGACY_MODULES):
                offenders.append(f"{path.relative_to(PROJECT_ROOT)}: {module}")

        self.assertEqual(
            offenders,
            [],
            "Entrypoints ainda importam módulos legados removidos: "
            + ", ".join(offenders),
        )


if __name__ == "__main__":
    unittest.main()
