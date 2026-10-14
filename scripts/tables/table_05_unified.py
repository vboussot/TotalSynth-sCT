#!/usr/bin/env python3
"""Table 5: the released unified MRI/CBCT-to-CT model by input domain and anatomical region."""

from _tables import ALL, CBCT, MRI, row, write

if __name__ == "__main__":
    rows = []
    for domain, branch, regions in (("MRI-to-CT", "Task_1/Unified", MRI), ("CBCT-to-CT", "Task_2/Unified", CBCT)):
        rows += [row(f"{domain}/{region}", branch, (region,)) for region in regions]
        rows += [row(f"{domain}/overall", branch, regions), r"\midrule"]
    write("table_05_unified.tex",
          "Evaluation of the released unified MRI/CBCT-to-CT model by input domain and anatomical region. "
          "Values report mean $\\pm$ standard deviation.",
          "tab:unified_mr_cbct_release_cv_metrics", "@{}lccccccc@{}", " & ".join(["Region", *ALL]), rows[:-1])
