# Shortcuts for the steps that take several commands. See docs/REPRODUCE.md.
PYTHON ?= python

.PHONY: help test paper-tables tables

help:
	@grep -E '^[a-z-]+:.*## ' Makefile | sed -E 's/:.*## /\t/' | expand -t 20

test:  ## repository integrity tests (no data needed)
	$(PYTHON) -m pytest -q

paper-tables:  ## the 6 tables of the paper, from its source (no data needed)
	$(PYTHON) scripts/tables/published_tables.py

tables:  ## Tables 2 to 6 from the patient-level metrics (no data needed)
	$(PYTHON) scripts/tables/table_02_summary.py
	$(PYTHON) scripts/tables/table_03_mri.py
	$(PYTHON) scripts/tables/table_04_cbct.py
	$(PYTHON) scripts/tables/table_05_unified.py
	$(PYTHON) scripts/tables/table_06_multimodal_hc.py
