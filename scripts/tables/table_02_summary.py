#!/usr/bin/env python3
"""Table 2: overall MAE, SSIM and PSNR of the released models and of Multimodal-HC fine-tuning."""

from _tables import MULTIMODAL_HC, CBCT, MRI, row, write

COLUMNS = ("MAE", "SSIM", "PSNR")
ROWS = (
    ("MRI-to-CT & Primary MRI/CT", "Task_1/Dedicated", MRI),
    ("CBCT-to-CT & Primary CBCT/CT", "Task_2/Dedicated", CBCT),
    ("Unified model & MRI inputs", "Task_1/Unified", MRI),
    ("Unified model & CBCT inputs", "Task_2/Unified", CBCT),
    ("MRI-to-CT, direct & Multimodal-HC", "Task_1/Unified", MULTIMODAL_HC),
    ("MRI-to-CT, fine-tuned & Multimodal-HC", "Task_1/Finetune", MULTIMODAL_HC),
)

if __name__ == "__main__":
    write("table_02_summary.tex",
          "Overall performance of released TotalSynth models and Multimodal-HC fine-tuning. Values report mean $\\pm$ standard deviation.",
          "tab:main_performance_summary", "@{}llccc@{}", "Model and setting & Evaluation domain & MAE (HU) & SSIM & PSNR (dB)",
          [row(label, branch, regions, COLUMNS) for label, branch, regions in ROWS], r"\small")
