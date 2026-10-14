#!/usr/bin/env python3
"""Table 3: the released MRI-to-CT model by anatomical region."""

from _tables import ALL, MRI, count, row, write

BRANCH = "Task_1/Dedicated"

if __name__ == "__main__":
    rows = [row(f"{region} ($n={count(BRANCH, (region,))}$)", BRANCH, (region,)) for region in MRI]
    rows += [r"\midrule", row(f"overall ($n={count(BRANCH, MRI)}$)", BRANCH, MRI)]
    write("table_03_mri.tex",
          "Evaluation of the released MRI-to-CT model by anatomical region. Values report mean $\\pm$ standard deviation. "
          "Case counts refer to the image-domain and Dice evaluation.",
          "tab:mri_to_ct_release_cv_metrics", "@{}lccccccc@{}", " & ".join(["Region", *ALL]), rows)
