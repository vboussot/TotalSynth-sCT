from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MSTD = re.compile(r"\\mstd\{([^}]+)\}\{([^}]+)\}")


def test_all_yaml_files_parse() -> None:
    for path in ROOT.glob("configs/**/*.y*ml"):
        assert yaml.safe_load(path.read_text(encoding="utf-8")) is not None, path


def test_paper_tables_are_present() -> None:
    numbers = sorted(int(path.name.split("_")[1]) for path in (ROOT / "tables").glob("table_*.tex"))
    assert numbers == list(range(1, 7))


def test_reported_figures_are_present() -> None:
    assert len(list((ROOT / "figures").glob("figure_[1-3]_*.png"))) == 3


def test_manifest_lists_the_four_models() -> None:
    with (ROOT / "models/manifest.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert sorted({row["model"] for row in rows}) == ["CBCT", "Finetune", "MR", "MR_CBCT"]
    assert len(rows) == 20 and all(len(row["sha256"]) == 64 for row in rows)


def test_held_out_lists() -> None:
    for task, cases, unified in ((1, 140, 136), (2, 150, 144)):
        folder = ROOT / f"data/splits/task_{task}"
        held_out = folder.joinpath("Validation.txt").read_text().split()
        assert len(held_out) == len(set(held_out)) == cases
        subset = folder.joinpath("Validation_unified.txt").read_text().split()
        assert len(subset) == unified and set(subset) <= set(held_out)
        assert set(folder.joinpath("Check.txt").read_text().split()) <= set(subset)


def test_metric_bundle_is_complete() -> None:
    assert len(list((ROOT / "results" / "raw" / "Evaluations").glob("**/Metric_TRAIN.json"))) == 102


def test_result_json_is_strictly_valid() -> None:
    def reject_non_finite(value: str) -> None:
        raise ValueError(value)

    for path in (ROOT / "results").glob("**/*.json"):
        json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_non_finite)


def test_executable_files_have_no_cluster_paths() -> None:
    forbidden = tuple("/" + name + "/" for name in ("scratch", "home", "gpfs", "mnt"))
    for base in (ROOT / "configs", ROOT / "scripts", ROOT / "src"):
        for path in base.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".yaml", ".yml"}:
                text = path.read_text(encoding="utf-8", errors="ignore")
                assert not any(item in text for item in forbidden), path


def test_script_tables_match_the_paper() -> None:
    """Every cell the scripts build from the paper's metrics is the paper's, to the last printed digit."""
    outputs = {2: "table_02_summary.tex", 3: "table_03_mri.tex", 4: "table_04_cbct.tex",
               5: "table_05_unified.tex", 6: "table_06_multimodal_hc.tex"}
    for number, output_name in outputs.items():
        reported_path = next((ROOT / "tables").glob(f"table_{number:02d}_*.tex"))
        rows = [[line for line in path.read_text(encoding="utf-8").splitlines() if "&" in line and r"\\" in line][1:]
                for path in (reported_path, ROOT / "tables" / "from_metrics" / output_name)]
        assert len(rows[0]) == len(rows[1]), number
        compared = 0
        for reported_row, built_row in zip(*rows):
            for column, (reported, built) in enumerate(zip(reported_row.split("&"), built_row.split("&"))):
                for mine, theirs in zip(MSTD.findall(built), MSTD.findall(reported)):
                    for value, reference in zip(mine, theirs):
                        step = 10 ** -len(reference.split(".")[1])
                        # Table 3's uncertainty agrees within 0.2 %
                        tolerance = abs(float(reference)) * 2e-3 if (number, column) == (3, 7) else step * 1.001
                        assert abs(float(value) - float(reference)) <= tolerance, (number, reported_row.split("&")[0])
                    compared += 1
        assert compared >= {2: 18, 3: 28, 4: 36, 5: 91, 6: 42}[number], number


def test_documented_files_exist() -> None:
    documents = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md")), *sorted(ROOT.glob("*/README.md")), ROOT / "Makefile"]
    for document in documents:
        text = document.read_text(encoding="utf-8")
        for path in set(re.findall(r"\b((?:scripts|configs|docs|tests|src)/[\w./-]+\.(?:py|md|yaml|yml))\b", text)):
            assert (ROOT / path).is_file(), f"{document.name} mentions {path}"
        for name in set(re.findall(r"\b((?:table_\d|figure_\d|published_tables)\w*\.py)\b", text)):
            assert list((ROOT / "scripts").rglob(name)), f"{document.name} mentions {name}"
