#!/usr/bin/env python3
"""Table 4: the released CBCT-to-CT model by anatomical region."""

from _tables import ALL, CBCT, count, row, write

BRANCH = "Task_2/Dedicated"

if __name__ == "__main__":
    rows = [row(f"{region} ($n={count(BRANCH, (region,))}$)", BRANCH, (region,)) for region in CBCT]
    rows += [r"\midrule", row(f"overall ($n={count(BRANCH, CBCT)}$)", BRANCH, CBCT)]
    write("table_04_cbct.tex",
          "Evaluation of the released CBCT-to-CT model by anatomical region. Values report mean $\\pm$ standard deviation.",
          "tab:cbct_to_ct_release_cv_metrics", "@{}lccccccc@{}", " & ".join(["Region", *ALL]), rows)
