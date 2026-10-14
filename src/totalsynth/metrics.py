"""The SAM metric of the tables, for KonfAI evaluation (``totalsynth.metrics:SAM_Perceptual``)."""

# No `from __future__ import annotations`: KonfAI reads these annotations at runtime.
import torch
import torch.nn.functional as F
from konfai.metric.measure import SAM_Perceptual as KonfAISAMPerceptual


class SAM_Perceptual(KonfAISAMPerceptual):
    """KonfAI's calibrated d_SAM as computed in the paper: one 512x512 tile per axial slice, the slice
    being zero-padded (0 HU) or cropped at the end of its axes. Both images are normalized with the
    reference's statistics."""

    def forward(self, output, *targets, attributes):
        def pad(tensor: torch.Tensor) -> torch.Tensor:
            height, width = tensor.shape[-2:]
            return F.pad(tensor, (0, 512 - width, 0, 512 - height), value=0)

        # KonfAI >= 1.8.7 passes the attributes of the targets only, which is what the normalization needs.
        assert len(attributes) == len(targets), "SAM_Perceptual needs KonfAI >= 1.8.7"
        return super().forward(pad(output), *(pad(target) for target in targets), attributes=attributes)
