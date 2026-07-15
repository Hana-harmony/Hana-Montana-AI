from __future__ import annotations

import math


def apply_source_logit_bias(
    probabilities: dict[str, float],
    source_type: str,
    biases_by_source: dict[str, dict[str, float]],
) -> dict[str, float]:
    biases = biases_by_source.get(source_type.upper())
    if not biases:
        return probabilities
    shifted = {
        label: math.log(max(float(probability), 1e-12)) + float(biases.get(label, 0.0))
        for label, probability in probabilities.items()
    }
    maximum = max(shifted.values())
    exponentials = {label: math.exp(value - maximum) for label, value in shifted.items()}
    total = sum(exponentials.values())
    return {label: value / total for label, value in exponentials.items()}
