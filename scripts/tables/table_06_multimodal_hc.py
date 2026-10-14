#!/usr/bin/env python3
"""Table 6: Multimodal-HC external evaluation before and after fine-tuning, for the in-phase and out-of-phase images."""

from _tables import ALL, MULTIMODAL_HC, row, write

if __name__ == "__main__":
    rows = []
    for setting, branch in (("Direct", "Task_1/Unified"), ("Fine-tuned", "Task_1/Finetune")):
        rows += [row(f"{setting} & {contrast}", branch, regions)
                 for contrast, regions in (("IN", MULTIMODAL_HC[:1]), ("OUT", MULTIMODAL_HC[1:]), ("Overall", MULTIMODAL_HC))]
        rows.append(r"\midrule")
    write("table_06_multimodal_hc.tex",
          "Multimodal-HC external evaluation before and after fine-tuning. Values report mean $\\pm$ standard deviation.",
          "tab:multimodal_hc_external_finetune", "@{}llccccccc@{}", " & ".join(["Setting", "Contrast", *ALL]), rows[:-1])
