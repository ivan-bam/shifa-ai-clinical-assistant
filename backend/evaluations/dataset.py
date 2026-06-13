"""
A small set of realistic Emergency Department cases used to evaluate the AI.

`expected_terms` lists clinically-relevant words we'd expect a competent
response to mention. The check passes if at least one appears.
"""
from dataclasses import dataclass, field


@dataclass
class EvalCase:
    name: str
    physician_input: str
    expected_terms: list[str] = field(default_factory=list)


CASES: list[EvalCase] = [
    EvalCase(
        name="chest_pain",
        physician_input=(
            "55yo male, central chest pain for 30 minutes, radiating to left arm, "
            "sweaty and nauseous"
        ),
        expected_terms=["ecg", "troponin", "aspirin"],
    ),
    EvalCase(
        name="sepsis",
        physician_input=(
            "70yo, fever 39C, confused, blood pressure 85/50, heart rate 120, "
            "looks very unwell"
        ),
        expected_terms=["lactate", "blood culture", "antibiotic", "fluid"],
    ),
    EvalCase(
        name="ankle_injury",
        physician_input=(
            "25yo, twisted ankle playing football, swelling, unable to bear weight"
        ),
        expected_terms=["x-ray", "fracture", "rice"],
    ),
]
