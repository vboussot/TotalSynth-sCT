# Manuscript source

`manuscript.tex` and `manuscript.bbl` are the source of the current version of the
paper ([arXiv:2609.13838](https://arxiv.org/abs/2609.13838));
`scripts/tables/published_tables.py` writes the 6 tables from it.

`SHA256SUMS` records hashes for the manuscript and its figures. Run it from the repository root with:

```bash
sha256sum --check paper/SHA256SUMS
```

The manuscript and its figures are distributed under the arXiv terms; the
Apache license of the code does not apply to them.
